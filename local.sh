docker build -t ml .
docker run --name ml-test ml:latest python -m unittest discover tests
docker run --name ml-server -p 5000:5000 ml:latest



ACCOUNT_ID=$(aws sts get-caller-identity --query 'Account' --output text)
REGION=$(aws configure get region)
ECR_REPOSITORY_URL="$ACCOUNT_ID.dkr.ecr.$REGION.amazonaws.com/ml"
LATEST_TAG=$(aws ecr describe-images --repository-name ml --query "sort_by(imageDetails,&imagePushedAt)[-1].imageTags[0]" --output text)
cp deployment.yaml deployment.yaml.bak
sed -i "s|{{ ECR_REPOSITORY_URL }}|$ECR_REPOSITORY_URL|g" deployment.yaml
sed -i "s|{{ TAG }}|$LATEST_TAG|g" deployment.yaml

kubectl apply -f deployment.yaml

mv deployment.yaml.bak deployment.yaml



kubectl port-forward deployment/ml-deployment 5000:5000
