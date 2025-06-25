import requests

url = "https://www.amfiindia.com/spages/NAVAll.txt"
output_file = "output.tsv"

response = requests.get(url)
lines = response.text.splitlines()

with open(output_file, "w", encoding="utf-8") as f:
    for line in lines:
        parts = line.strip().split(";")
        if len(parts) == 6:
            scheme_name = parts[3].strip()
            nav = parts[4].strip()
            if scheme_name and nav:
                f.write(f"{scheme_name};{nav}\n")

print(f"Saved to {output_file}")
