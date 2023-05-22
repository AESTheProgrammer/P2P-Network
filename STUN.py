import redis
import socketserver
import json
from http.server import HTTPServer, BaseHTTPRequestHandler

# Redis configuration
REDIS_HOST = 'localhost'
REDIS_PORT = 6379
REDIS_DB = 0

# HTTP server configuration
HOST = 'localhost'
PORT = 8000

# Redis client initialization
redis_client = redis.Redis(host=REDIS_HOST, port=REDIS_PORT, db=REDIS_DB)
# Ping the Redis server
try:
    response = redis_client.ping()
    if response:
        print("Connected to Redis")
    else:
        print("Failed to connect to Redis")
except redis.exceptions.ConnectionError as e:
    print("Connection error:", e)
# print(redis_client.get("armin"))

class MyHTTPRequestHandler(BaseHTTPRequestHandler):
    def do_POST(self):
        if self.path == '/users':
            content_length = int(self.headers['Content-Length'])
            post_data = self.rfile.read(content_length)
            data = json.loads(post_data.decode())

            user_id = data.get('user-id')
            address = data.get('address')

            if user_id and address:
                redis_client.set(user_id, address)
                user_id = redis_client.get(user_id)
                print(user_id)
                self.send_response(200)
                self.send_header('Content-type', 'text/plain')
                self.end_headers()
                self.wfile.write(b'User ID and address saved successfully')
            else:
                self.send_response(400)
                self.send_header('Content-type', 'text/plain')
                self.end_headers()
                self.wfile.write(b'Invalid request data')
        else:
            self.send_response(404)
            self.send_header('Content-type', 'text/plain')
            self.end_headers()
            self.wfile.write(b'Endpoint not found')

    def do_GET(self):
        if self.path == '/users':
            user_ids = redis_client.keys()
            print(user_ids)
            user_ids = [user_id.decode() for user_id in user_ids]
            response = dict()
            for index, user_id in enumerate(user_ids):
                response[user_id] = index
            json_data = json.dumps(response).encode()
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            self.wfile.write(json_data)
        elif self.path.startswith('/users/'):
            user_id = self.path[7:]

            ip_address = redis_client.get(user_id)

            if ip_address:
                self.send_response(200)
                self.send_header('Content-type', 'text/plain')
                self.end_headers()
                self.wfile.write(ip_address)
            else:
                self.send_response(404)
                self.send_header('Content-type', 'text/plain')
                self.end_headers()
                self.wfile.write(b'User ID not found')
        else:
            self.send_response(404)
            self.send_header('Content-type', 'text/plain')
            self.end_headers()
            self.wfile.write(b'Endpoint not found')


def main():
    # Create an HTTP server with the custom request handler
    httpd = HTTPServer((HOST, PORT), MyHTTPRequestHandler)
    # Start the server
    print(f'Server running on {HOST}:{PORT}')
    httpd.serve_forever()


if __name__ == "__main__":
    main()
