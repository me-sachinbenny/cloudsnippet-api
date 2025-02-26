"""Example data for API documentation."""

TOOL_EXAMPLE = {
    "name": "Docker",
    "slug": "docker",
    "description": "Containerization platform",
    "image": "https://example.com/docker.png",
    "overview": "Docker is a platform for developing, shipping, and running applications in containers.",
    "troubleshooting": [
        {
            "id": "1",
            "title": "Container not starting",
            "description": "The container fails to start due to a configuration issue.",
            "solution": "Check the container logs using 'docker logs <container_id>'."
        }
    ],
    "best_practices": [
        {
            "id": "1",
            "title": "Use multi-stage builds",
            "description": "Reduce image size and improve build efficiency."
        }
    ],
    "implementations": [
        {
            "id": "1",
            "title": "Setting up a basic Docker container",
            "description": "Steps to create a simple container.",
            "steps": [
                "Install Docker.",
                "Create a Dockerfile.",
                "Build the image.",
                "Run the container."
            ]
        }
    ],
    "tagline": "Empowering developers with containerization.",
    "category": "Containerization"
}

TOOL_UPDATE_EXAMPLE = {
    "description": "Updated description",
    "best_practices": ["New best practice"]
}

TOOL_BRIEF_EXAMPLE = {
    "id": "507f1f77bcf86cd799439011",
    "name": "Docker",
    "image": "https://example.com/docker.png",
    "description": "Containerization platform",
    "slug": "docker"
}

TOOL_DETAIL_EXAMPLE = {
    "id": "507f1f77bcf86cd799439011",
    "name": "Docker",
    "description": "Containerization platform",
    "image": "https://example.com/docker.png",
    "overview": "Docker is a platform for developing, shipping, and running applications in containers.",
    "troubleshooting": [
        {
            "id": "1",
            "title": "Container not starting",
            "description": "The container fails to start due to a configuration issue.",
            "solution": "Check the container logs using 'docker logs <container_id>'."
        }
    ],
    "best_practices": [
        {
            "id": "1",
            "title": "Use multi-stage builds",
            "description": "Reduce image size and improve build efficiency."
        }
    ],
    "implementations": [
        {
            "id": "1",
            "title": "Setting up a basic Docker container",
            "description": "Steps to create a simple container.",
            "steps": [
                "Install Docker.",
                "Create a Dockerfile.",
                "Build the image.",
                "Run the container."
            ]
        }
    ],
    "created_at": "2025-02-17T10:00:00Z",
    "updated_at": "2025-02-17T11:00:00Z"
}

TOOL_LIST_EXAMPLE = {
    "items": [TOOL_BRIEF_EXAMPLE],
    "total": 100,
    "skip": 0,
    "limit": 10
}
