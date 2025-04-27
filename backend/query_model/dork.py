import random

# Predefined Google Dork templates
DORK_TEMPLATES = [
    'site:{target} inurl:admin',
    'site:{target} intitle:"index of"',
    'site:{target} ext:sql | ext:txt | ext:log',
    'site:{target} inurl:login',
    'site:{target} filetype:pdf | filetype:doc | filetype:xls',
    'site:{target} intext:"password" | intext:"admin"',
    'site:{target} inurl:wp-admin',
    'site:{target} -www inurl:ftp',
    'site:{target} ext:json | ext:config -git',
    'site:{target} inurl:php?id=',
    'site:{target} confidential OR sensitive filetype:xls OR filetype:csv',
    'inurl:/phpmyadmin site:{target}',
    'intitle:"WebcamXP" | intitle:"webcam 7" site:{target}',
    'site:pastebin.com intext:{target}',
]

def generate_dorks(target_text):
    """Generates multiple dork queries based on input text."""
    dorks = [template.format(target=target_text) for template in DORK_TEMPLATES]
    return dorks

def save_dorks_to_file(dorks, filename="dork_queries.txt"):
    """Saves generated dorks to a text file."""
    with open(filename, "w") as file:
        for dork in dorks:
            file.write(dork + "\n")
    print(f"\n✅ Dork queries saved to {filename}")

if __name__ == "__main__":
    target_text = input("🔍 Enter the target keyword or domain (e.g., example.com): ")
    
    # Generate dorks
    generated_dorks = generate_dorks(target_text)
    
    # Print results
    print("\n🔹 Generated Google Dork Queries:")
    for dork in generated_dorks:
        print(dork)
    
    # Save results to file
    save_dorks_to_file(generated_dorks)
