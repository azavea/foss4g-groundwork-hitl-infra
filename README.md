# GroundWork, Raster Vision, and STAC FOSS4G Workshop Infrastructure

This repo contains ansible and terraform code required to spin up a bunch of EC2 instances with:

- Raster Vision container images (so no one has to pull them)
- A sample tif
- A workbook

Its purpose is to create a bunch of identical EC2 instances capable of running an example notebook exposed to the internet.

You can create and configure the EC2 instances with the following steps:

- ~~create a file called `variables.secret` with a public key in the `notebook_server_public_key` variable and some integer in the `instance_count` variable.~~
- change the `default` variable in `terraform/variables.tf` to reflect the number of instances you want (temporary)
- run `./scripts/infra plan` and `./scripts/infra apply` to create the EC2 instances. You will be prompted to enter a `notebook_server_public_key` (.pub)
- copy the list of IPs into new `ansible/inventory` file e.g.:
    ```
    [instance_ips]
    x.xx.xx.xx
    xx.xxx.xxx.xxx
    ```
- console into the ansible container: `docker-compose run --rm --entrypoint sh ansible`
- create a secrets file with some AWS credentials (these will be used to pull a tif from s3 into the EC2 instance):
  - create a `yaml` file at `ansible/secrets.yaml` with `aws_access_key_id` and `aws_secret_access_key` objects with your keys
  - encrypt that file from inside the  using `ansible-vault`: `ansible-vault encrypt --output secrets.enc secrets.yaml`
  - delete your plain text yaml file
- run the playbook: `ansible-playbook -e @secrets.enc --ask-vault-pass -i inventory --private-key /root/.ssh/[[your-key-here]] setup-wrkshop.yml`
- users can access notebook at `https://{ip address}:8888`