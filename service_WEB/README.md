# (Dis)AsTeR - WEB Service

This submodule specifically will host the Flask interface we develop on AWS. The current micro-service is integrated on the web through a *AWS Elastic Beanstalk*, which gives us some flexibility regarding network architecture. Ultimately, this platform is purposedly designed to be modular, and fully integrated with the *Cloud Foundry* SQL database and APIs we developed.

> Code Specificity: Using `application.py` as the filename and providing a callable `application` object (the Flask object, in this case) allows Elastic Beanstalk to easily find your application's code.

## SSL Context Generation

```bash
openssl genrsa 2048 > xxx.key
openssl req -new -x509 -nodes -sha256 -days 365 -key xxx.key -out xxx.crt
```

```bash
Country Name (2 letter code) [AU]:US
State or Province Name (full name) [Some-State]:California
Locality Name (eg, city) []:Berkeley
Organization Name (eg, company) [Internet Widgits Pty Ltd]:AsTeR
Organizational Unit Name (eg, section) []:serviceWEB
Common Name (e.g. server FQDN or YOUR name) []:elasticbeanstalk.com
Email Address []:meryll_dindin@berkeley.edu
```

```basth
aws iam upload-server-certificate --server-certificate-name aws-aster --certificate-body file://configs/host_crt.crt --private-key file://configs/host_key.pem
```

```bash
{
    "ServerCertificateMetadata": {
        "Path": "/",
        "ServerCertificateName": "aws-aster",
        "ServerCertificateId": "ASCAXA5BMRBFET2U6OFX7",
        "Arn": "arn:aws:iam::482985412682:server-certificate/aws-aster",
        "UploadDate": "2019-07-16T16:57:41Z",
        "Expiration": "2020-07-15T16:29:19Z"
    }
}
```

## AWS Elastic Beanstalk

```bash
eb init --region us-west-1 --profile xxx
eb create serviceWEB
eb open
```

## Logfiles

```bash
Creating application version archive "app-190710_104234".
Uploading serviceWEB/app-190710_104234.zip to S3. This may take a while.
Upload Complete.
Environment details for: serviceWEB
  Application name: serviceWEB
  Region: us-west-1
  Deployed Version: app-190710_104234
  Environment ID: e-dxim4mrgx6
  Platform: arn:aws:elasticbeanstalk:us-west-1::platform/Python 3.6 running on 64bit Amazon Linux/2.8.6
  Tier: WebServer-Standard-1.0
  CNAME: UNKNOWN
  Updated: 2019-07-10 17:42:37.861000+00:00
Printing Status:
2019-07-10 17:42:36    INFO    createEnvironment is starting.
2019-07-10 17:42:38    INFO    Using xxx as Amazon S3 storage bucket for environment data.
2019-07-10 17:43:03    INFO    Created security group named: xxx
2019-07-10 17:43:18    INFO    Created load balancer named: xxx
2019-07-10 17:43:19    INFO    Created security group named: xxx
2019-07-10 17:43:19    INFO    Created Auto Scaling launch configuration named: xxx
2019-07-10 17:54:40    INFO    Created Auto Scaling group named: xxx
2019-07-10 17:54:40    INFO    Waiting for EC2 instances to launch. This may take a few minutes.
2019-07-10 17:54:40    INFO    Created Auto Scaling group policy named: xxx
2019-07-10 17:54:40    INFO    Created CloudWatch alarm named: xxx
2019-07-10 17:54:41    INFO    Created CloudWatch alarm named: xxx
2019-07-10 17:55:32    INFO    Application available at serviceWEB.jzh2fab4hr.us-east-2.elasticbeanstalk.com.
2019-07-10 17:55:32    INFO    Successfully launched environment: serviceWEB
```