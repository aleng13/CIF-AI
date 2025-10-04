# This first block tells Terraform we need the Google Cloud provider
terraform {
  required_providers {
    google = {
      source  = "hashicorp/google"
      version = "~> 5.0"
    }
  }
}

# This block connects Terraform to your specific project and region
provider "google" {
  project = var.project_id
  region  = var.region
}