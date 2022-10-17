# Semantic Search API Documentation
---
## Root

**URL** : `/`

**Method** : `GET`

**Auth required** : NO

### Success Response

**Code** : `200 OK`

---
## Add Text

Add new sentences to storage.

**URL** : `/add-text`

**Method** : `POST`

**Auth required** : NO

**requestBody**

    content: application/json
    anyOf: string, Array[string]

**Request Samples**

```json
[
    "გველსა ხვრელით ამოიყვანს", 
    "ენა ტკბილად მოუბარი"
]
```
```json
"გველსა ხვრელით ამოიყვანს"
```

### Success Response

**Code** : `201 CREATED`

### Error Response

**Code** : `422 Unprocessable Entity`

---
## Search Text

Searc keywords in texts.

**URL** : `/search-text`

**Method** : `GET`

**Auth required** : NO

**requestBody**

    content: application/json
    text (required): string
    topk: integer (Default: -1)
    threshold: number (Default: 0.5)

**Request Samples**

```json
{
    "text": "გველი",
    "threshold": 0.9,
    "topk": 10
}
```

### Success Response

**Code** : `200 OK`

### Error Response

**Code** : `422 Unprocessable Entity`

---
## Add Image

Add new image to the storage.

**URL** : `/add-image-url`

**Method** : `POST`

**Auth required** : NO

**requestBody**

    content: application/json
    anyOf: string, Array[string]

**Request Samples**

```json
["image_url"]
```

### Success Response

**Code** : `201 CREATED`

### Error Response

**Code** : `422 Unprocessable Entity`

---
## Search Image

Search similar images according to existing image.

**URL** : `/`

**Method** : `GET`

**Auth required** : NO

**requestBody**

    content: application/json
    id (required): integer
    topk: integer (Default: -1)
    threshold: number (Default: 0.5)

**Request Samples**

```json
{
    "id":0,
    "threshold":0.9,
    "topk":10
}
```

### Success Response

**Code** : `200 OK`

### Error Response

**Code** : `422 Unprocessable Entity`
