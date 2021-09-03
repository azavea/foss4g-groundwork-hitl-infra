resource "aws_instance" "notebook_server" {
  # Ubuntu 20.04, 2021-08-25
  ami = "ami-03b5637245555e13d"
  # 4 cpu, 8gb memory, decent sized ssd
  instance_type = "c6gd.xlarge"

  key_name                    = aws_key_pair.notebook_server_key_pair.key_name
  associate_public_ip_address = true
  count                       = var.instance_count

  tags = {
    Name = "Notebook server"
  }
}

resource "aws_key_pair" "notebook_server_key_pair" {
  public_key = var.notebook_server_public_key
  key_name   = "foss4g_notebook_server_key"
}

output "instance_ips" {
  value = aws_instance.notebook_server.public_ip
}