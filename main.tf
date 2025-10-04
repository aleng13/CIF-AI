################################################################################
# NETWORKING - CUSTOM VPC
################################################################################

# This resource creates the main "fence" for our project (the VPC)
resource "google_compute_network" "main_vpc" {
  name                    = "vpc-main"
  auto_create_subnetworks = false # This is a security best practice
}

# This resource creates a specific subnet inside our VPC for the Mumbai region
resource "google_compute_subnetwork" "main_subnetwork" {
  name          = "subnet-main"
  ip_cidr_range = "10.0.1.0/24"
  region        = var.region
  network       = google_compute_network.main_vpc.id
}

################################################################################
# IAM - PERMISSIONS FOR YOUR 4-PERSON TEAM
################################################################################

# IMPORTANT: Give YOURSELF the "Owner" role.
resource "google_project_iam_member" "project_owner" {
  project = var.project_id
  role    = "roles/owner"
  member  = "user:alengscaria13@gmail.com" # <-- This is you.
}

# Give your first teammate the "Editor" role.
resource "google_project_iam_member" "developer_1" {
  project = var.project_id
  role    = "roles/editor"
  member  = "user:aaronittyipe670@gmail.com" # <-- REPLACE with your first teammate's email
}

# Give your second teammate the "Editor" role.
resource "google_project_iam_member" "developer_2" {
  project = var.project_id
  role    = "roles/editor"
  member  = "user:alwinthomas200424@gmail.com" # <-- REPLACE with your second teammate's email
}

# Give your third teammate the "Editor" role.
resource "google_project_iam_member" "developer_3" {
  project = var.project_id
  role    = "roles/editor"
  member  = "user:abrahammadamana@gmail.com" # <-- REPLACE with your third teammate's email
}

################################################################################
# DATABASE - CLOUD SQL FOR POSTGRESQL (Private)
################################################################################

#Our AI application will need to connect to the database. 
#To do that, it needs a password. This is the system that creates and protects that password.

# This creates a secure place to store the database password
resource "google_secret_manager_secret" "db_password" {
  secret_id = "db-password"

  replication {
    user_managed {
      replicas {
        location = var.region   # e.g. "asia-south1" for Mumbai
      }
    }
  }
}


# This generates a random password
resource "random_password" "password" {
  length  = 16
  special = true
}

# This puts the new random password into Secret Manager
resource "google_secret_manager_secret_version" "db_password_version" {
  secret      = google_secret_manager_secret.db_password.id
  secret_data = random_password.password.result
}

# This is the special networking "plumbing" for our private database
resource "google_compute_global_address" "private_ip_address" {
  name          = "private-ip-for-sql"
  purpose       = "VPC_PEERING"
  address_type  = "INTERNAL"
  prefix_length = 16
  network       = google_compute_network.main_vpc.id
}

resource "google_service_networking_connection" "private_vpc_connection" {
  network                 = google_compute_network.main_vpc.id
  service                 = "servicenetworking.googleapis.com"
  reserved_peering_ranges = [google_compute_global_address.private_ip_address.name]
}

# This is the blueprint for the actual PostgreSQL database instance
resource "google_sql_database_instance" "main_db" {
  name             = "email-mvp-db"
  database_version = "POSTGRES_14"
  region           = var.region

  settings {
    tier = "db-g1-small" # This is a small, cost-effective size for an MVP
    ip_configuration {
      ipv4_enabled    = false # No public IP address - VERY IMPORTANT for security
      private_network = google_compute_network.main_vpc.id
    }
  }

  # This makes sure the networking is ready before trying to create the database
  depends_on = [google_service_networking_connection.private_vpc_connection]
}


################################################################################
# STORAGE - GCS BUCKET
################################################################################

resource "google_storage_bucket" "knowledge_docs" {
  name                        = "${var.project_id}-knowledge-docs" # Creates a unique bucket name
  location                    = var.region
  uniform_bucket_level_access = true
}

################################################################################
# AI - VERTEX AI & DEDICATED SERVICE ACCOUNT
################################################################################

# Service Account for our Cloud Run application.
# This is like an ID badge for our app to wear.
resource "google_service_account" "sa_app" {
  account_id   = "sa-app"
  display_name = "Service Account for Cloud Run App"
}

# Give the App's "ID badge" permission to use Vertex AI
resource "google_project_iam_member" "sa_app_vertex_user" {
  project = var.project_id
  role    = "roles/aiplatform.user"
  member  = "serviceAccount:${google_service_account.sa_app.email}"
}

# Give the App's "ID badge" permission to read the database password from Secret Manager
resource "google_project_iam_member" "sa_app_secret_accessor" {
  project = var.project_id
  role    = "roles/secretmanager.secretAccessor"
  member  = "serviceAccount:${google_service_account.sa_app.email}"
}

# Create the blueprint for the AI's "magical card catalog" (the Vector Search Index)
# Note: This only creates the index resource. You still need to upload documents and
# tell the AI to "read" them later. That's an application-level task.
resource "google_vertex_ai_index" "email_mvp_index" {
  display_name = "email-mvp-vector-index"
  description  = "Vector index for knowledge documents"
  region       = var.region

  metadata {
    contents_delta_uri = "gs://${google_storage_bucket.knowledge_docs.name}/vector-index"
    config {
      dimensions = 768 # This is a standard dimension size for many popular text models
      approximate_neighbors_count = 150
      algorithm_config {
        tree_ah_config {}
      }
    }
  }
}

# Create the "Librarian's desk" (the Index Endpoint) where the app can ask questions
resource "google_vertex_ai_index_endpoint" "email_mvp_index_endpoint" {
  display_name = "email-mvp-vector-index-endpoint"
  region       = var.region
}

################################################################################
# EVENTING - PUB/SUB & EVENTARC TRIGGER
################################################################################

# This creates a Pub/Sub topic - a channel for receiving notifications from Gmail
resource "google_pubsub_topic" "gmail_topic" {
  name = "gmail-inbox-events"
}

# This creates a Pub/Sub topic - a channel for receiving notifications from Gmail
resource "google_eventarc_trigger" "gmail_trigger" {
  name     = "trigger-gmail-to-cloud-run"
  location = var.region

  matching_criteria {
    attribute = "type"
    value     = "google.cloud.pubsub.topic.v1.messagePublished"
  }

  destination {
    cloud_run_service {
      service = "email-processor-svc"
      region  = var.region
    }
  }

  service_account = google_service_account.sa_app.email

  transport {
    pubsub {
      topic = google_pubsub_topic.gmail_topic.id
    }
  }
}

################################################################################
# DEPLOYMENT - CLOUD RUN & VPC CONNECTOR
################################################################################

# Serverless VPC Connector is required for Cloud Run to reach the private DB
resource "google_vpc_access_connector" "serverless" {
  name          = "serverless-connector"
  region        = var.region
  ip_cidr_range = "10.8.0.0/28" # Must not overlap with other subnets
  network       = google_compute_network.main_vpc.id
}

# This is the blueprint for our main application service (the "house")
# We use a placeholder "hello world" image for now. Our CI/CD pipeline will
# replace it with our real application later.
resource "google_cloud_run_v2_service" "email_processor" {
  name     = "email-processor-svc"
  location = var.region

  template {
    # Run as our dedicated application service account (the "ID badge" we made)
    service_account = google_service_account.sa_app.email

    containers {
      image = "us-docker.pkg.dev/cloudrun/container/hello" # Placeholder image
    }

    # Connect to our VPC to access the Cloud SQL database
    vpc_access {
      connector = google_vpc_access_connector.serverless.id
      egress    = "ALL_TRAFFIC"
    }
  }
}