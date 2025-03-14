import json

# email and one pass pass
# Data to be saved into a JSON file (it can be a dictionary, list, etc.)
data= {
  "email": "georgesque360@gmail.com",
  "password": "bnri jovy nxhu sdop",
"SECRET_KEY": "django-insecure-ivmq#&9ei*!l9o3rlq_$57^w4!(xh*%jd*-io#yqu_xed&5k!-"
}

# Specify the name of the file
filename = './encrypt/e_sif.json'

# Open the file in write mode and dump the data into the file
with open(filename, 'w') as file:
    json.dump(data, file, indent=3)

print(f"JSON file '{filename}' created successfully.")
