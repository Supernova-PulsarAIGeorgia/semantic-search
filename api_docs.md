# Semantic Search API Documentation

## Add Text
---

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

## Success Response

**Code** : `201 OK`

## Error Response

**Code** : `422 Unprocessable Entity`