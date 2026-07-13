#!/usr/bin/env python3
from __future__ import annotations

import json
import sys
from datetime import datetime, timezone
from pathlib import Path

SCRIPT_DIR = Path(__file__).resolve().parent
if str(SCRIPT_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPT_DIR))

from track1d_local_storage import ensure_track1e_schema, load_local_storage_config
from track1d_repository import Track1DRepository


ProductResponse = tuple[int, dict[str, object]]
ALLOWED_PRODUCT_STATUS = {"active", "inactive", "archived"}
ALLOWED_PRODUCT_FIELDS = {"name", "category", "description", "status", "metadata"}


def _iso_now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def error_response(
    status_code: int,
    error: str,
    message: str,
    field_errors: dict[str, str] | None = None,
) -> ProductResponse:
    payload: dict[str, object] = {
        "error": error,
        "message": message,
        "status_code": status_code,
    }
    if field_errors:
        payload["field_errors"] = field_errors
    return status_code, payload


def parse_json_object(body: bytes) -> tuple[dict[str, object] | None, ProductResponse | None]:
    if not body:
        return {}, None
    try:
        data = json.loads(body.decode("utf-8"))
    except (UnicodeDecodeError, json.JSONDecodeError):
        return None, error_response(400, "validation_error", "Request body must be valid JSON.")
    if not isinstance(data, dict):
        return None, error_response(422, "validation_error", "Request body must be a JSON object.")
    return data, None


def _open_repository(database_path: str | None = None) -> tuple[Track1DRepository, str]:
    config = load_local_storage_config(database_path_override=database_path)
    ensure_track1e_schema(config)
    return Track1DRepository.connect(config.database_path), str(config.database_path)


def _validate_product_payload(
    data: dict[str, object],
    *,
    partial: bool = False,
) -> tuple[dict[str, object] | None, ProductResponse | None]:
    field_errors: dict[str, str] = {}
    normalized: dict[str, object] = {}

    if partial:
        unknown_fields = sorted(set(data) - ALLOWED_PRODUCT_FIELDS)
        if unknown_fields:
            for field_name in unknown_fields:
                field_errors[field_name] = "Unknown field."
        if not data:
            return None, error_response(422, "validation_error", "At least one allowed field is required.")
        if field_errors:
            return None, error_response(422, "validation_error", "Product update payload is invalid.", field_errors)
    else:
        for required_field in ("name", "category"):
            if required_field not in data:
                field_errors[required_field] = "Missing required field."
        unknown_fields = sorted(set(data) - (ALLOWED_PRODUCT_FIELDS))
        for field_name in unknown_fields:
            field_errors[field_name] = "Unknown field."
        if field_errors:
            return None, error_response(422, "validation_error", "Product payload is invalid.", field_errors)

    if "name" in data:
        if not isinstance(data["name"], str) or not data["name"].strip():
            field_errors["name"] = "Field must be a non-empty string."
        else:
            normalized["name"] = data["name"].strip()

    if "category" in data:
        if not isinstance(data["category"], str) or not data["category"].strip():
            field_errors["category"] = "Field must be a non-empty string."
        else:
            normalized["category"] = data["category"].strip()

    if "description" in data:
        if not isinstance(data["description"], str):
            field_errors["description"] = "Field must be a string."
        else:
            normalized["description"] = data["description"]
    elif not partial:
        normalized["description"] = ""

    if "status" in data:
        if not isinstance(data["status"], str) or data["status"] not in ALLOWED_PRODUCT_STATUS:
            field_errors["status"] = "Field must be one of active, inactive, archived."
        else:
            normalized["status"] = data["status"]
    elif not partial:
        normalized["status"] = "active"

    if "metadata" in data:
        if not isinstance(data["metadata"], dict):
            field_errors["metadata"] = "Field must be a JSON object."
        else:
            normalized["metadata"] = data["metadata"]
    elif not partial:
        normalized["metadata"] = {}

    if field_errors:
        message = "Product update payload is invalid." if partial else "Product payload is invalid."
        return None, error_response(422, "validation_error", message, field_errors)
    return normalized, None


def _validate_affiliate_offer_payload(
    data: dict[str, object],
    repository: Track1DRepository,
) -> tuple[dict[str, object] | None, ProductResponse | None]:
    field_errors: dict[str, str] = {}
    normalized: dict[str, object] = {}

    for required_field in ("product_id", "source_id", "offer_url"):
        if required_field not in data:
            field_errors[required_field] = "Missing required field."

    allowed_fields = {
        "product_id",
        "source_id",
        "offer_url",
        "title",
        "price",
        "currency",
        "commission_rate",
        "status",
        "metadata",
    }
    for field_name in sorted(set(data) - allowed_fields):
        field_errors[field_name] = "Unknown field."

    if field_errors:
        return None, error_response(422, "validation_error", "Affiliate offer payload is invalid.", field_errors)

    product_id = data["product_id"]
    if not isinstance(product_id, str) or not product_id.strip():
        field_errors["product_id"] = "Field must be a non-empty string."
    elif not repository.product_exists(product_id.strip()):
        field_errors["product_id"] = "Referenced product does not exist."
    else:
        normalized["product_id"] = product_id.strip()

    source_id = data["source_id"]
    if not isinstance(source_id, str) or not source_id.strip():
        field_errors["source_id"] = "Field must be a non-empty string."
    elif not repository.source_exists(source_id.strip()):
        field_errors["source_id"] = "Referenced source does not exist."
    else:
        normalized["source_id"] = source_id.strip()

    offer_url = data["offer_url"]
    if not isinstance(offer_url, str) or not offer_url.strip():
        field_errors["offer_url"] = "Field must be a non-empty string."
    else:
        normalized["offer_url"] = offer_url.strip()

    title = data.get("title", "")
    if not isinstance(title, str):
        field_errors["title"] = "Field must be a string."
    else:
        normalized["title"] = title

    price = data.get("price")
    if price is None:
        normalized["price"] = None
    elif not isinstance(price, (int, float)):
        field_errors["price"] = "Field must be numeric."
    else:
        normalized["price"] = float(price)

    currency = data.get("currency", "")
    if not isinstance(currency, str):
        field_errors["currency"] = "Field must be a string."
    else:
        normalized["currency"] = currency

    commission_rate = data.get("commission_rate")
    if commission_rate is None:
        normalized["commission_rate"] = None
    elif not isinstance(commission_rate, (int, float)):
        field_errors["commission_rate"] = "Field must be numeric."
    else:
        normalized["commission_rate"] = float(commission_rate)

    status = data.get("status", "active")
    if not isinstance(status, str) or status not in ALLOWED_PRODUCT_STATUS:
        field_errors["status"] = "Field must be one of active, inactive, archived."
    else:
        normalized["status"] = status

    metadata = data.get("metadata", {})
    if not isinstance(metadata, dict):
        field_errors["metadata"] = "Field must be a JSON object."
    else:
        normalized["metadata"] = metadata

    if field_errors:
        return None, error_response(422, "validation_error", "Affiliate offer payload is invalid.", field_errors)
    return normalized, None


def handle_product_create(body: bytes, *, database_path: str | None = None) -> ProductResponse:
    payload, error = parse_json_object(body)
    if error is not None:
        return error
    assert payload is not None
    normalized, validation_error = _validate_product_payload(payload, partial=False)
    if validation_error is not None:
        return validation_error
    assert normalized is not None

    repository, _ = _open_repository(database_path)
    try:
        timestamp = _iso_now()
        normalized["id"] = repository.next_product_id()
        normalized["created_at"] = timestamp
        normalized["updated_at"] = timestamp
        created = repository.create_product(normalized)
    finally:
        repository.close()
    return 200, created


def handle_product_list(*, database_path: str | None = None) -> ProductResponse:
    repository, _ = _open_repository(database_path)
    try:
        products = repository.list_products()
    finally:
        repository.close()
    return 200, {"products": products, "count": len(products)}


def handle_product_get(product_id: str, *, database_path: str | None = None) -> ProductResponse:
    repository, _ = _open_repository(database_path)
    try:
        product = repository.get_product(product_id)
    finally:
        repository.close()
    if product is None:
        return error_response(404, "not_found", f"Product not found: {product_id}")
    return 200, product


def handle_product_patch(product_id: str, body: bytes, *, database_path: str | None = None) -> ProductResponse:
    payload, error = parse_json_object(body)
    if error is not None:
        return error
    assert payload is not None
    normalized, validation_error = _validate_product_payload(payload, partial=True)
    if validation_error is not None:
        return validation_error
    assert normalized is not None

    repository, _ = _open_repository(database_path)
    try:
        if not repository.product_exists(product_id):
            return error_response(404, "not_found", f"Product not found: {product_id}")
        normalized["updated_at"] = _iso_now()
        updated = repository.update_product(product_id, normalized)
    finally:
        repository.close()
    assert updated is not None
    return 200, updated


def handle_affiliate_offer_create(body: bytes, *, database_path: str | None = None) -> ProductResponse:
    payload, error = parse_json_object(body)
    if error is not None:
        return error
    assert payload is not None

    repository, _ = _open_repository(database_path)
    try:
        normalized, validation_error = _validate_affiliate_offer_payload(payload, repository)
        if validation_error is not None:
            return validation_error
        assert normalized is not None
        timestamp = _iso_now()
        normalized["id"] = repository.next_affiliate_offer_id()
        normalized["created_at"] = timestamp
        normalized["updated_at"] = timestamp
        created = repository.create_affiliate_offer(normalized)
    finally:
        repository.close()
    return 200, created


def handle_affiliate_offer_list(*, database_path: str | None = None) -> ProductResponse:
    repository, _ = _open_repository(database_path)
    try:
        offers = repository.list_affiliate_offers()
    finally:
        repository.close()
    return 200, {"affiliate_offers": offers, "count": len(offers)}
