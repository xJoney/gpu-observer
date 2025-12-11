terraform {
  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 4.16"
    }
  }
  required_version = ">= 1.2.0"
}

provider "aws" {
  region = "us-east-1"
}


# VARIABLES
variable "ALERT_EMAIL" {
  description = "Email for budget alerts"
  type        = string
  sensitive   = true
}

variable "GRAFANA_PASSWORD" {
  description = "Password for Grafana Admin"
  type        = string
  sensitive   = true
}

variable "EMAIL_TO" {
  description = "target email address"
  type        = string
  sensitive   = true
}

variable "EMAIL_FROM" {
  description = "Gmail address for alertmanager"
  type        = string
  sensitive   = true
}

variable "EMAIL_PASS" {
  description = "Google App Password for alertmanager"
  type        = string
  sensitive   = true
}




# Automatically find home IP address
data "http" "myip" {
  url = "http://ipv4.icanhazip.com"
}

resource "aws_security_group" "gpu_observer_sg" {
  name        = "gpu-observer-sg"
  description = "Strict firewall for GPU Observer"

  # SSH port 22 my IP only
  ingress {
    from_port   = 22
    to_port     = 22
    protocol    = "tcp"
    cidr_blocks = ["${chomp(data.http.myip.response_body)}/32"]
  }

  # Grafana port 3001 my IP only
  ingress {
    from_port   = 3001
    to_port     = 3001
    protocol    = "tcp"
    cidr_blocks = ["${chomp(data.http.myip.response_body)}/32"]
  }

  # Data Ingestion port 8081 opened to take in data from gpu data from any machine
  ingress {
    from_port   = 8081
    to_port     = 8081
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }

  # Allows everything outgoing which allows downloading updates etc..
  egress {
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }
}

# email notification for when costs are >80% of budget
resource "aws_budgets_budget" "cost_guard" {
  name              = "project-gpu-observer-budget"
  budget_type       = "COST"
  limit_amount      = "10.0"
  limit_unit        = "USD"
  time_unit         = "MONTHLY"

  notification {
    comparison_operator        = "GREATER_THAN"
    threshold                  = 80
    threshold_type             = "PERCENTAGE"
    notification_type          = "ACTUAL"
    subscriber_email_addresses = [var.ALERT_EMAIL]
  }
}


resource "aws_instance" "app_server" {
  ami           = "ami-04b70fa74e45c3917" # using ubuntu 24.04 LTS (us-east-1)
  instance_type = "t3.small"              

  key_name      = "my-ssh-key"            
  vpc_security_group_ids = [aws_security_group.gpu_observer_sg.id]

  # Startup Script
  user_data = <<-EOF
              #!/bin/bash
              apt-get update
              apt-get install -y docker.io docker-compose-v2 git
              systemctl start docker
              systemctl enable docker

              git clone https://github.com/xjoney/gpu-observer.git /home/ubuntu/gpu-observer
              cd /home/ubuntu/gpu-observer

              cat <<EOT > .env
              GRAFANA_PASSWORD=${var.GRAFANA_PASSWORD}
              EMAIL_TO=${var.ALERT_EMAIL}
              EMAIL_FROM=${var.EMAIL_FROM}
              EMAIL_USER=${var.EMAIL_FROM}
              EMAIL_PASS=${var.EMAIL_PASS}
              EOT              
              docker compose up -d --build
              EOF

  tags = {
    Name = "GPU-Observer-Server"
  }
}

# output for ip
output "public_ip" {
  value = aws_instance.app_server.public_ip
}