import pytest
from django.core.files.uploadedfile import SimpleUploadedFile

from apps.products.models import ProductImage
from apps.products.tests.conftest import make_product

pytestmark = pytest.mark.django_db

# A complete, minimal 1x1 transparent GIF — real bytes so Pillow's
# ImageField validation (triggered on save) accepts it as a genuine image.
TINY_GIF = (
    b"GIF89a\x01\x00\x01\x00\x80\x00\x00\x00\x00\x00\xff\xff\xff!\xf9\x04\x01\x00\x00\x00\x00,"
    b"\x00\x00\x00\x00\x01\x00\x01\x00\x00\x02\x02D\x01\x00;"
)


def _gif(name="test.gif"):
    return SimpleUploadedFile(name, TINY_GIF, content_type="image/gif")


@pytest.fixture(autouse=True)
def media_root(settings, tmp_path):
    # Uploaded test images land in a throwaway pytest tmp_path instead
    # of the project's real backend/media/ directory.
    settings.MEDIA_ROOT = tmp_path


def _upload(api_client, product_id, **extra):
    payload = {"image_url": _gif(), **extra}
    return api_client.post(f"/api/products/mine/{product_id}/images/", payload, format="multipart")


def test_upload_requires_ownership(api_client, vendor, pending_vendor, category):
    other_product = make_product(pending_vendor, category, slug="other", sku="SKU-OTHER")
    api_client.force_authenticate(user=vendor.user)

    response = _upload(api_client, other_product.pk)

    assert response.status_code == 404


def test_upload_image(api_client, vendor, category):
    product = make_product(vendor, category)
    api_client.force_authenticate(user=vendor.user)

    response = _upload(api_client, product.pk, is_primary=True)

    assert response.status_code == 201
    assert response.json()["is_primary"] is True
    assert ProductImage.objects.filter(product=product).count() == 1


def test_second_primary_image_unsets_first(api_client, vendor, category):
    product = make_product(vendor, category)
    api_client.force_authenticate(user=vendor.user)

    _upload(api_client, product.pk, is_primary=True)
    _upload(api_client, product.pk, is_primary=True)

    primaries = ProductImage.objects.filter(product=product, is_primary=True)
    assert primaries.count() == 1


def test_images_appear_on_public_product_detail(api_client, vendor, category):
    product = make_product(vendor, category)
    api_client.force_authenticate(user=vendor.user)
    _upload(api_client, product.pk, is_primary=True)

    api_client.force_authenticate(user=None)
    response = api_client.get(f"/api/products/{product.slug}/")

    assert response.status_code == 200
    assert len(response.json()["images"]) == 1


def test_delete_image(api_client, vendor, category):
    product = make_product(vendor, category)
    api_client.force_authenticate(user=vendor.user)
    created = _upload(api_client, product.pk)
    image_id = created.json()["id"]

    response = api_client.delete(f"/api/products/mine/{product.pk}/images/{image_id}/")

    assert response.status_code == 204
    assert not ProductImage.objects.filter(pk=image_id).exists()
