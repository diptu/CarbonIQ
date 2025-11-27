
## 🐳  Dockarize

1.  contanirize
- a. Build (Linux/AWS ready)
```bash
docker build --platform linux/amd64 \
  -t diptu/carboniq:auth_version_0.0.1 \
  -f auth_service/Dockerfile .

```
- b. Build (Local Mac ready)

```bash
docker build -t auth_service  \
    -f auth_service/Dockerfile .

```
2. Run Dockarize containner
```bash
 docker run -p 8000:8000 --env-file auth_service/app/.env auth_service
```

## push to hub

0. veiw images
```bash
docker images
```
1. update tag with version if required

```bash
docker tag auth_service:latest diptu/carboniq:auth_version_0.0.1 # here user_service is the hub reponame
```
2.
a. login to docker hub

```bash
docker login
```
push image to hub

```bash
 docker push diptu/carboniq:auth_version_0.0.1
```


## Host to AWS EC2

[Host to Aws](https://www.youtube.com/watch?v=X0lnToYN21k&list=PLKnIA16_RmvZ41tjbKB2ZnwchfniNsMuQ&index=12)
 1. create an EC2 instance
 2. Connect to the EC2 instance

 3. Run the following commands
  a. sudo apt-get update
  b. sudo apt-get install -y docker.io
  c. sudo systemctl start docker
  d. sudo systemctl enable docker
  e. sudo usermod -aG docker $USER
  f. exit

  ```bash
    sudo apt-get update && \
    sudo apt-get install -y docker.io && \
    sudo systemctl start docker && \
    sudo systemctl enable docker && \
    sudo usermod -aG docker $USER && \
    exit

  ```

 4. Restart a new connection to EC2 instance
 5. Run the following commands
  a. docker pull diptu/carboniq:auth_version_0.0.1
  b. docker run -p 8000:8000  diptu/carboniq:auth_version_0.0.1

    ```bash
     docker pull diptu/carboniq:auth_version_0.0.1 && \
     docker run -p 8000:8000  diptu/carboniq:auth_version_0.0.1
    ```
 6. change security group settings
 7. Check the API
 8. Change the frontend code

# [Link to access](http://3.25.65.83:8000/)
