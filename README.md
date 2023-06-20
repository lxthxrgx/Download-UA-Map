# Download-UA-Map

### The program performs the following steps:

1. Downloads files with the .pbf extension.
2. Decodes the downloaded files.
3. Extracts cadastral numbers from the decoded files and stores them in a database.
4. Sends a request to the Django website to obtain detailed information about the cadastral number.
5. Writes the received information to the database.

### The Protocol Buffer Binary Format (.pbf) files were downloaded from the website [Kadastr.com](https://kadastr.live/#5/48.43/32.77).
