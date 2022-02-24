# GroundWork, Raster Vision, and STAC FOSS4G Workshop Infrastructure

This repo contains ansible and terraform code required to spin up a bunch of EC2 instances with:

- Raster Vision container images (so no one has to pull them)
- A sample tif
- A workbook

Its purpose is to create a bunch of identical EC2 instances capable of running an example notebook exposed to the internet.

You can create and configure the EC2 instances with the following steps:

- create a file called `variables.secret` with a public key in the `notebook_server_public_key` variable and some integer in the `instance_count` variable. This should have the syntax of a .tfvars file (see https://www.terraform.io/language/values/variables#variable-definitions-tfvars-files for details). Example:
  ```
  instance_count = 2
  notebook_server_public_key = "ssh-rsa ..."
  ```
- run `./scripts/infra plan` and `./scripts/infra apply` to create the EC2 instances
- copy the list of IPs into new `ansible/inventory` file e.g.:
    ```
    [instance_ips]
    x.xx.xx.xx
    xx.xxx.xxx.xxx
    ```
- console into the ansible container: `docker-compose run --rm --entrypoint sh ansible`
- create a secrets file with some AWS credentials (these will be used to pull a tif from s3 into the EC2 instance):
  - create a `yaml` file at `ansible/secrets.yaml` with `aws_access_key_id` and `aws_secret_access_key` objects with your keys
  ```yaml
  aws_access_key_id: "xxxx..."
  aws_secret_access_key: "xxxx..."
  ```
  - encrypt that file from inside the  using `ansible-vault`: `ansible-vault encrypt --output secrets.enc secrets.yaml`, you will be prompted to create a password that you will use in a later step
  - delete your plain text yaml file
- run the playbook: `ansible-playbook -e @secrets.enc --ask-vault-pass -i inventory --private-key /root/.ssh/{name of private key file (e.g. id_rsa)} setup-workshop.yml`
- users can access notebook at `https://{ip address}:8888`, password for notebooks is `foss4g2021`
- make sure to shut down and delete ec2 instances when done