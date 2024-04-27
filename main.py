from Website import create_app

app = create_app()
if __name__ == "__main__":
    # whenever changes are made to the python code , the server reruns --> debug=True
    app.run(debug=True)# made changes
