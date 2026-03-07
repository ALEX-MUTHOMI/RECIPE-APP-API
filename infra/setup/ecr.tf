##############################################
# Create ECR repos for storing docker images #
##############################################

resource "aws_ecr_repository" "app" {
  name                 = "recipe-app-api-app"
  image_tag_mutability = "MUTABLE"
  force_delete         = true # "FALSE" FOR REAL DEPLOYMENTS
  # Might not ADD "TRUE"  on a production instance

  image_scanning_configuration {
    #NOTE: UPDATE TO TRUE FOR REAL DEPLOYMENT
    scan_on_push = false
  }
}

resource "aws_ecr_repository" "proxy" {
  name                 = "recipe-app-api-proxy"
  image_tag_mutability = "MUTABLE"
  force_delete         = true # "FALSE" FOR REAL DEPLOYMENTS
  # Might not ADD "TRUE"  on a production instance

  image_scanning_configuration {
    #NOTE: UPDATE TO TRUE FOR REAL DEPLOYMENT
    scan_on_push = false
  }
}
