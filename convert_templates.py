import os
import re
import shutil

src_dir = r"src\main\resources\templates"
dst_dir = "templates"

if not os.path.exists(dst_dir):
    os.makedirs(dst_dir)

def convert_thymeleaf_to_jinja(content):
    # 1. th:href="@{/css/style.css}" -> href="{{ url_for('static', filename='css/style.css') }}"
    content = re.sub(r'th:href="@\{/css/style\.css\}"', r'href="{{ url_for(\'static\', filename=\'css/style.css\') }}"', content)
    
    # 2. th:action="@{/path}" -> action="{{ url_for('main.path_name') }}"
    # Manually fix specific ones to map to our flask routes
    content = content.replace('th:action="@{/login}"', 'action="{{ url_for(\'main.login\') }}"')
    content = content.replace('th:action="@{/order}"', 'action="{{ url_for(\'main.place_order\') }}"')
    content = content.replace('th:action="@{/payment/confirm}"', 'action="{{ url_for(\'main.payment\') }}"') # payment handles post
    content = content.replace('th:action="@{/vending/login}"', 'action="{{ url_for(\'main.vending_login\') }}"')
    content = content.replace('th:action="@{/vending/dispense/rice}"', 'action="{{ url_for(\'main.dispense\', item=\'rice\') }}"')
    content = content.replace('th:action="@{/vending/dispense/wheat}"', 'action="{{ url_for(\'main.dispense\', item=\'wheat\') }}"')
    content = content.replace('th:action="@{/vending/dispense/sugar}"', 'action="{{ url_for(\'main.dispense\', item=\'sugar\') }}"')
    
    # Links
    content = content.replace('th:href="@{/logout}"', 'href="{{ url_for(\'main.logout\') }}"')
    content = content.replace('th:href="@{/vending/login}"', 'href="{{ url_for(\'main.vending_login\') }}"')
    
    # Variables: th:text="${var}" -> >{{ var }}<
    # This regex is a bit simplistic but works for exact tags like <span th:text="${foo}">0</span> -> <span>{{ foo }}</span>
    # Wait, the best way is to replace `th:text="${expr}"` with nothing and put `{{ expr }}` inside the tag.
    content = re.sub(r'<([^>]+)\s+th:text="\$\{([^}]+)\}"([^>]*)>([^<]*)</', r'<\1 \3>{{ \2 }}</', content)
    # Also handle strings: th:text="'Welcome, ' + ${user.username}" -> >Welcome, {{ user.username }}<
    content = re.sub(r'<([^>]+)\s+th:text="\'Welcome, \' \+ \$\{([^}]+)\}"([^>]*)>([^<]*)</', r'<\1 \3>Welcome, {{ \2 }}</', content)
    content = re.sub(r'<([^>]+)\s+th:text="\'📞 \' \+ \$\{([^}]+)\} \+ \'  \|  📍 \' \+ \$\{([^}]+)\}"([^>]*)>([^<]*)</', r'<\1 \4>📞 {{ \2 }}  |  📍 {{ \3 }}</', content)
    content = re.sub(r'<([^>]+)\s+th:text="\'📟 \' \+ \$\{([^}]+)\}"([^>]*)>([^<]*)</', r'<\1 \3>📟 {{ \2 }}</', content)
    content = re.sub(r'<([^>]+)\s+th:text="\$\{([^}]+)\} \+ \' kg\'"([^>]*)>([^<]*)</', r'<\1 \3>{{ \2 }} kg</', content)

    # Conditionals
    content = re.sub(r'<([^>]+)\s+th:if="\$\{([^}]+)\}"([^>]*)>', r'{% if \2 %}\n<\1 \3>', content)
    # close the if... this is hard to do with regex alone.
    # Better to manually fix the ones we know about. Let's just do a basic string replacement since we have the files.
    return content

for filename in os.listdir(src_dir):
    if filename.endswith(".html"):
        with open(os.path.join(src_dir, filename), "r", encoding="utf-8") as f:
            content = f.read()
        
        # Don't overwrite vending-login.html as we already wrote it
        if filename == "vending-login.html":
            continue
            
        content = convert_thymeleaf_to_jinja(content)
        
        # Fix missing endifs
        if filename == "login.html":
            content = content.replace('{% if errorMessage %}\n<div  class="alert alert-danger">{{ errorMessage }}</div>', '{% if errorMessage %}\n<div class="alert alert-danger">{{ errorMessage }}</div>\n{% endif %}')
            content = content.replace('{% if logoutMessage %}\n<div  class="alert alert-success">{{ logoutMessage }}</div>', '{% if logoutMessage %}\n<div class="alert alert-success">{{ logoutMessage }}</div>\n{% endif %}')
            content = content.replace('th:if="${errorMessage}"', '{% if errorMessage %}')
            content = content.replace('th:if="${logoutMessage}"', '{% if logoutMessage %}')
            # manual text replacement
            content = re.sub(r'<div th:if="\$\{errorMessage\}" class="alert alert-danger" th:text="\$\{errorMessage\}"></div>', '{% if errorMessage %}<div class="alert alert-danger">{{ errorMessage }}</div>{% endif %}', content)
            content = re.sub(r'<div th:if="\$\{logoutMessage\}" class="alert alert-success" th:text="\$\{logoutMessage\}"></div>', '{% if logoutMessage %}<div class="alert alert-success">{{ logoutMessage }}</div>{% endif %}', content)
            
        with open(os.path.join(dst_dir, filename), "w", encoding="utf-8") as f:
            f.write(content)
            
print("Templates converted.")
