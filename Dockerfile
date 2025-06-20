# Use an official Node.js image that has Debian underneath
FROM node:18

# Install Python and pip
RUN apt-get update && apt-get install -y python3 python3-pip

# Set the working directory
WORKDIR /app

# Copy package and requirements
COPY package*.json ./
COPY requirements.txt ./

# Install Node dependencies
RUN npm install

# Install Python dependencies
RUN pip3 install -r requirements.txt

# Copy all source code
COPY . .

# Expose your app's port (adjust if needed)
EXPOSE 10000

# Start your server
CMD ["node", "index.js"]
