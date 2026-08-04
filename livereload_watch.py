from livereload import Server

server = Server()

server.watch('Frontend/Users/**/*.html')
server.watch('Frontend/Admin/**/*.html')
server.watch('Photos/**/*')
server.watch('backend/**/*.py')

server.serve(host='127.0.0.1', port=35729, open_url=False)
