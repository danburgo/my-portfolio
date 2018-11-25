import json
import boto3
from botocore.client import Config
import StringIO
import zipfile
import mimetypes

def lambda_handler(event, context):
    try:
        sns = boto3.resource('sns')
        topic = sns.Topic('arn:aws:sns:us-east-1:923583669602:portfolioDeployTopic')

        s3 = boto3.resource('s3')
        #s3 = boto3.resource('s3', config=Config(signature_version='s3v4'))

        portfolio_bucket = s3.Bucket('portfolio.danburdeinick.info')
        build_bucket = s3.Bucket('portfoliobuild.danburdeinick.info')

        portfolio_zip = StringIO.StringIO()
        build_bucket.download_fileobj('portfoliobuild.zip',portfolio_zip)

        with zipfile.ZipFile(portfolio_zip) as myzip:
            for nm in myzip.namelist():
                obj = myzip.open(nm)
                portfolio_bucket.upload_fileobj(obj,nm,ExtraArgs={'ContentType': mimetypes.guess_type(nm)[0]})
                portfolio_bucket.Object(nm).Acl().put(ACL='public-read')
        topic.publish(Subject="Deployment success", Message="The portfolio project was deployed successfully")

    except:
            topic.publish(Subject="Deployment failure", Message="The portfolio was NOT successul")
            raise
    return {
        'statusCode': 200,
        'body': json.dumps('Deploy success')
    }
