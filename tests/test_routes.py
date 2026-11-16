import io


def test_rejects_non_csv_file(app):
    client = app.test_client()
    resp = client.post(
        "/upload",
        data={"file": (io.BytesIO(b"hello"), "notes.txt")},
        content_type="multipart/form-data",
        follow_redirects=True,
    )
    assert b"Only .csv files are allowed" in resp.data


def test_summary_api_with_no_data(app):
    client = app.test_client()
    data = client.get("/api/summary").get_json()
    assert data["selected"] is None
    assert data["categories"] == []