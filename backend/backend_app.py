from flask import Flask, jsonify, request, Response
from flask_cors import CORS

app = Flask(__name__)
CORS(app)  # This will enable CORS for all routes

POSTS = [
    {"id": 1, "title": "First post", "content": "This is the first post."},
    {"id": 2, "title": "Second post", "content": "This is the second post."},
]


@app.route('/api/posts', methods=['GET'])
def get_posts() -> tuple[Response, int]:
    """
    Return all blog posts with optional sorting.

    Posts can be sorted by "title" or "content" in ascending or
    descending order. If no sort field is provided, the original
    order is preserved.
    """
    sort_field = request.args.get("sort")
    direction = request.args.get("direction", "asc")

    if sort_field is None:
        return jsonify(POSTS), 200

    if sort_field not in ("title", "content"):
        return jsonify({
            "error": "Invalid sort field. Use 'title' or 'content'."
        }), 400

    if direction not in ("asc", "desc"):
        return jsonify({
            "error": "Invalid direction. Use 'asc' or 'desc'."
        }), 400

    sorted_posts = sorted(
        POSTS,
        key=lambda post: post[sort_field].lower(),
        reverse=direction == "desc"
    )

    return jsonify(sorted_posts), 200


@app.route('/api/posts', methods=['POST'])
def make_posts() -> tuple[Response, int]:
    """
    Create a new blog post.

    The request must contain a non-empty "title" and "content".
    The title must be unique. A new unique ID is generated
    automatically before the post is added.
    """
    new_post = request.get_json()
    missing_fields = [
        field for field in ("title", "content")
        if not new_post.get(field)
    ]

    if missing_fields:
        return jsonify({
            "error": f"Missing {' and '.join(missing_fields)}"
        }), 400

    unique_post = check_unique_name(new_post)
    if unique_post:
        new_post["id"] = (find_available_id())
        POSTS.append(new_post)
        return jsonify(new_post), 201
    return jsonify({"error": "Title already exists"}), 400


@app.route('/api/posts/<int:post_id>', methods=['DELETE'])
def delete_post(post_id: int) -> tuple[Response, int]:
    """
    Delete a blog post by ID.

    Returns a success message if the post exists, or a 404 error
    if no post with the given ID can be found.
    """
    for index, post in enumerate(POSTS):
        if post["id"] == post_id:
            POSTS.pop(index)
            return jsonify({
                "message": f"Post with id {post_id} has been deleted successfully."
            }), 200

    return jsonify({
                "error": f"Post with id {post_id} not found."
            }), 404


@app.route('/api/posts/<int:post_id>', methods=['PUT'])
def update_post(post_id: int) -> tuple[Response, int]:
    """
    Update an existing blog post by ID.

    Only non-empty values for "title" and "content" are applied.
    Missing or empty fields keep their current values.
    Returns the updated post with status 200, or a 404 error
    if no post with the given ID exists.
    """
    new_post = request.get_json()
    for post in POSTS:
        if post["id"] == post_id:
            updates = [
                field for field in ("title", "content")
                if new_post.get(field)
            ]
            for update in updates:
                post[update] = new_post[update]
            return jsonify(post), 200

    return jsonify({
        "error": f"Post with id {post_id} not found."
    }), 404


@app.route('/api/posts/search', methods=['GET'])
def search_post() -> tuple[Response, int]:
    """
    Search blog posts by title or content.

    Search terms are provided through optional query parameters.
    Matching is case-insensitive and posts are returned when either
    the title or content contains the corresponding search term.
    """
    title = request.args.get("title", "").lower().strip()
    content = request.args.get("content", "").lower().strip()
    results = []

    for post in POSTS:
        title_match = bool(title) and title in post["title"].lower()
        content_match = bool(content) and content in post["content"].lower()

        if title_match or content_match:
            results.append(post)

    return jsonify(results), 200


# Helpers

def find_available_id() -> int:
    """
    Return the smallest available positive integer ID.

    Existing post IDs are collected and checked starting from 1
    until an unused ID is found.
    """
    used_ids = {post["id"] for post in POSTS}

    new_id = 1
    while new_id in used_ids:
        new_id += 1

    return new_id


def check_unique_name(new_post) -> bool:
    """
    Check whether the title of a new post is unique.

    Returns False if another post already uses the same title,
    otherwise returns True.
    """
    for post in POSTS:#
        if post["title"] == new_post["title"]:
            return False
    return True


if __name__ == '__main__':
    app.run(host="0.0.0.0", port=5002, debug=True)
