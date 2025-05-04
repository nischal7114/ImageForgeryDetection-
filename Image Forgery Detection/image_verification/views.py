import os
import io
import json
import hashlib
import piexif
import imagehash
import base64
from PIL import Image as PILImage
from io import BytesIO
from xhtml2pdf import pisa
from weasyprint import HTML
from django.http import HttpResponse
from django.utils import timezone
from django.template.loader import get_template
from cryptography.hazmat.primitives.asymmetric import ed25519
from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse
from django.contrib.auth.decorators import login_required
from .models import CaseImage
from .forms import CaseImageForm, ImageVerificationForm
from case_management.models import Case
from activity_log.models import log_activity
from user_management.decorators import group_required

# Utility to convert GPS data to decimal format
def convert_gps_to_decimal(gps_data):
    try:
        degrees = gps_data[0][0] / gps_data[0][1]
        minutes = gps_data[1][0] / gps_data[1][1]
        seconds = gps_data[2][0] / gps_data[2][1]
        return round(degrees + (minutes / 60) + (seconds / 3600), 6)
    except (IndexError, ZeroDivisionError, TypeError):
        return None

@login_required
def image_delete(request, image_id):
    image = get_object_or_404(CaseImage, id=image_id)
    case_id = image.case.id
    if request.method == "POST":
        image.delete()
        log_activity(request.user, 'Deleted image', case=image.case, image=image)
        return redirect(reverse('case_detail', args=[case_id]))
    return render(request, 'image_verification/image_confirm_delete.html', {'image': image})

@login_required
@group_required('Investigator')
def image_upload(request):
    case_id = request.GET.get('case_id')
    case = get_object_or_404(Case, id=case_id)

    if request.method == 'POST':
        form = CaseImageForm(request.POST, request.FILES)
        if form.is_valid():
            case_image = form.save(commit=False)
            case_image.case = case
            case_image.uploaded_by = request.user

            uploaded_image = request.FILES['image']
            image_data = uploaded_image.read()

            # Calculate SHA-256 hash
            sha256_hash = hashlib.sha256(image_data).hexdigest()
            case_image.sha256_hash = sha256_hash

            # Generate Perceptual Hash
            image = PILImage.open(io.BytesIO(image_data))
            perceptual_hash = str(imagehash.phash(image))
            case_image.perceptual_hash = perceptual_hash

            # Generate Ed25519 Digital Signature
            private_key = ed25519.Ed25519PrivateKey.generate()
            signature = private_key.sign(sha256_hash.encode())
            case_image.digital_signature = signature.hex()

            # Extract Metadata
            metadata_dict = extract_image_metadata(image, case_image.digital_signature)
            case_image.metadata = json.dumps(metadata_dict, indent=4)

            case_image.save()
            log_activity(request.user, 'Uploaded image', case=case, image=case_image)
            return redirect('case_detail', case_id=case.id)
    else:
        form = CaseImageForm()
    return render(request, 'image_verification/image_upload.html', {'form': form, 'case': case})

def extract_image_metadata(image, signature_hex):
    metadata_dict = {}
    try:
        if image.format == "JPEG":
            exif_data = image.info.get("exif", None)
            if exif_data:
                exif_dict = piexif.load(exif_data)
            else:
                exif_dict = {"0th": {}, "Exif": {}, "GPS": {}, "1st": {}, "thumbnail": None}

            exif_dict["0th"][piexif.ImageIFD.ImageDescription] = f"Signature: {signature_hex}"
            for group in ["0th", "Exif", "GPS", "1st"]:
                for key, value in exif_dict[group].items():
                    if isinstance(value, bytes):
                        value = value.decode('utf-8', errors='ignore')
                    metadata_dict[piexif.TAGS[group][key]["name"]] = normalize_metadata(value)

            if "GPSLatitude" in exif_dict["GPS"] and "GPSLongitude" in exif_dict["GPS"]:
                gps_latitude = convert_gps_to_decimal(exif_dict["GPS"][piexif.GPSIFD.GPSLatitude])
                gps_longitude = convert_gps_to_decimal(exif_dict["GPS"][piexif.GPSIFD.GPSLongitude])
                metadata_dict["GPSLatitudeDecimal"] = gps_latitude
                metadata_dict["GPSLongitudeDecimal"] = gps_longitude
        print("Extracted Metadata:", metadata_dict)
    except Exception as e:
        metadata_dict = {"error": str(e)}
    return metadata_dict

def normalize_metadata(value):
    if isinstance(value, tuple):
        return list(value)
    elif isinstance(value, list):
        return [normalize_metadata(v) for v in value]
    elif isinstance(value, dict):
        return {k: normalize_metadata(v) for k, v in value.items()}
    return value

def compare_metadata(original_metadata, uploaded_metadata):
    """Compare two metadata dictionaries after normalizing nested lists and tuples."""
    comparison_results = {}
    for key in original_metadata:
        original_value = normalize_metadata(original_metadata.get(key))
        uploaded_value = normalize_metadata(uploaded_metadata.get(key))
        comparison_results[key] = {
            "original_value": original_value,
            "uploaded_value": uploaded_value,
            "match": original_value == uploaded_value
        }
    return comparison_results

def normalize_metadata_value(value):
    """Normalize metadata value for comparison."""
    if isinstance(value, (list, tuple)):
        return [normalize_metadata_value(v) for v in value]
    elif isinstance(value, dict):
        return {k: normalize_metadata_value(v) for k, v in value.items()}
    return value

def image_delete(request, image_id):
    image = get_object_or_404(CaseImage, id=image_id)
    case_id = image.case.id
    if request.method == "POST":
        image.delete()
        log_activity(request.user, 'Deleted image', case=image.case, image=image)
        return redirect(reverse('case_detail', args=[case_id]))
    return render(request, 'image_verification/image_confirm_delete.html', {'image': image})

@login_required
@group_required('Viewer')
def image_list(request):
    images = CaseImage.objects.all().order_by('-uploaded_at')
    return render(request, 'image_verification/image_list.html', {'images': images})

@login_required
@group_required('Viewer')
def image_detail(request, image_id):
    image = get_object_or_404(CaseImage, id=image_id)
    
    # Handle JSON decoding for metadata with a fallback
    try:
        metadata = json.loads(image.metadata) if image.metadata else {}
    except json.JSONDecodeError:
        metadata = {"error": "Metadata could not be decoded"}

    return render(request, 'image_verification/image_detail.html', {
        'image': image,
        'metadata': metadata,
    })

@login_required
@group_required('Investigator')
def image_verification(request, image_id):
    original_image = get_object_or_404(CaseImage, id=image_id)
    result = None

    if request.method == 'POST' and 'uploaded_image' in request.FILES:
        uploaded_image = request.FILES['uploaded_image']
        
        # Read the image data and calculate SHA-256 and Perceptual Hash
        image_data = uploaded_image.read()
        sha256_hash = hashlib.sha256(image_data).hexdigest()
        uploaded_phash = str(imagehash.phash(PILImage.open(io.BytesIO(image_data))))

        # Convert image data to base64 for displaying in the template
        uploaded_image_base64 = base64.b64encode(image_data).decode('utf-8')
        
        # Metadata Extraction and Normalization
        uploaded_metadata = normalize_metadata(extract_image_metadata(PILImage.open(io.BytesIO(image_data)), ''))
        print("Uploaded Metadata:", uploaded_metadata)
        original_metadata = normalize_metadata(json.loads(original_image.metadata)) if original_image.metadata else {}

        # Remove ImageDescription from metadata for comparison
        if 'ImageDescription' in uploaded_metadata:
            del uploaded_metadata['ImageDescription']
        if 'ImageDescription' in original_metadata:
            del original_metadata['ImageDescription']

        # Comparison Results
        hash_match = sha256_hash == original_image.sha256_hash
        perceptual_match = uploaded_phash == original_image.perceptual_hash
        metadata_match = uploaded_metadata == original_metadata

        result = {
            "sha256_match": hash_match,
            "perceptual_match": perceptual_match,
            "metadata_match": metadata_match,
            "uploaded_sha256": sha256_hash,
            "uploaded_phash": uploaded_phash,
            "uploaded_metadata": uploaded_metadata,
            "uploaded_image_base64": uploaded_image_base64,
        }
        request.session['verification_result'] = result
        log_activity(request.user, 'Verified image', case=original_image.case, image=original_image, details=f'Verification result: {result}')
    return render(request, 'image_verification/verify_image.html', {
        'original_image': original_image,
        'result': result,
        'original_metadata': json.loads(original_image.metadata) if original_image.metadata else {}
    })

@login_required
@group_required('Viewer')
def generate_pdf(request, image_id):
    result = request.session.get('verification_result')
    if not result:
        return HttpResponse("Verification result not found in session.", status=404)

    original_image = get_object_or_404(CaseImage, id=image_id)
    
    # Convert the original image to base64
    with open(original_image.image.path, "rb") as image_file:
        original_image_base64 = base64.b64encode(image_file.read()).decode('utf-8')

    context = {
        'original_image': original_image,
        'original_image_base64': original_image_base64,  # Pass base64-encoded image to template
        'result': result,
        'original_metadata': json.loads(original_image.metadata) if original_image.metadata else {},
        'current_date': timezone.now().strftime('%Y-%m-%d %H:%M:%S')
    }

    template = get_template('image_verification/pdf_report.html')
    html = template.render(context)
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="Verification_Report_{image_id}.pdf"'

    pisa_status = pisa.CreatePDF(html, dest=response)
    if pisa_status.err:
        return HttpResponse("Error generating PDF", status=500)
    return response

def homepage(request):
    return render(request, 'homepage.html')