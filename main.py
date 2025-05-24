from http.server import HTTPServer, BaseHTTPRequestHandler
import json
import os
import urllib.parse
import petname #to generate player names

# --- Configuration ---
HOST = '0.0.0.0'
PORT = 8080
HTML_FILE = 'page.html'
WINNING_CLICKS = 50

# --- Server State ---
user_data = {}  #eg {"User 1": 0, "User 2": 5}
game_over = False
winning_user = None


# --- Request Handler ---
class SimplifiedGetRequestHandler(BaseHTTPRequestHandler):

    def send_json_response(self, status_code, data):  #helper function
        self.send_response(status_code)
        self.send_header('Content-type', 'application/json')
        self.send_header('Cache-Control', 'no-store, max-age=0')
        self.end_headers()
        self.wfile.write(json.dumps(data).encode('utf-8'))

    # handle various GET requests like
    # / --> serves page.html
    # /register_user --> responds with json data including new user id
    # /user_click?user_id=pet-name&clicks=3 --> updates click data, responds with json data including all user clicks
    def do_GET(self):
        global game_over, winning_user  #to allow updating global variables
        parsed_url = urllib.parse.urlparse(self.path)  
        query_params = urllib.parse.parse_qs(parsed_url.query)

        if parsed_url.path == '/':
            with open(HTML_FILE, 'rb') as f:
                self.send_response(200)
                self.send_header('Content-type', 'text/html')
                self.end_headers()
                self.wfile.write(f.read())

        elif parsed_url.path == '/register_user':
            user_id = petname.generate()    #random name like 'curious-dolphin'
            user_data[user_id] = 0
            response_payload = {
                "yourID": user_id,
                "userData": user_data,
                "winningClicks": WINNING_CLICKS,
                "gameOver": game_over,
                "winner": winning_user
            }
            self.send_json_response(200, response_payload)
            print(f"Registered new user: {user_id}")

        elif parsed_url.path == '/user_click':
            if not game_over:
                user_id = query_params['user_id'][0]
                clicks = int(query_params['clicks'][0])
                user_data[user_id] = clicks
                if user_data[user_id] >= WINNING_CLICKS:
                    game_over = True
                    winning_user = user_id
            response_payload = {
                "userData": user_data,
                "gameOver": game_over,
                "winner": winning_user
            }
            self.send_json_response(200, response_payload)

        else:  #not one of the 3 types of requests we can handle
            self.send_error(404, "Stop! Hammer time!")

    def log_message(self, format, *args):
        return


def run_server():
    server_address = (HOST, PORT)
    httpd = HTTPServer(server_address,
                       SimplifiedGetRequestHandler)  # Use new handler
    print(f"Starting Server on {HOST}:{PORT}")
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        print("\nServer stopping...")
        httpd.server_close()


if __name__ == '__main__':
    run_server()
