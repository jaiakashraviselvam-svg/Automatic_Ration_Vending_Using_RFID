import sys

with open('templates/vending-machine.html', 'r', encoding='utf-8') as f:
    html = f.read()

# 1. Forms
forms_old = '<form id="form-sugar" action="{{ url_for(\'main.dispense\', item=\'sugar\') }}" method="post" style="display:none;"></form>'
forms_new = forms_old + '\n<form id="form-oil" action="{{ url_for(\'main.dispense\', item=\'oil\') }}" method="post" style="display:none;"></form>\n<form id="form-soap" action="{{ url_for(\'main.dispense\', item=\'soap\') }}" method="post" style="display:none;"></form>\n<form id="form-detergent" action="{{ url_for(\'main.dispense\', item=\'detergent\') }}" method="post" style="display:none;"></form>'
html = html.replace(forms_old, forms_new)

# 2. Badges
badges_new = '''
        {% if order.oilLiters > 0 and not order.oilDispensed %}
        <div class="vm-badge avail" onclick="dispense('oil','4')">
            <div class="vm-bi">&#x1F6E2;&#xFE0F;</div><div class="vm-bn">OIL [4]</div>
            <div class="vm-bq">{{ order.oilLiters }} L</div><div class="vm-bs">&#9679; READY</div>
        </div>
        {% elif order.oilLiters > 0 and order.oilDispensed %}
        <div class="vm-badge done">
            <div class="vm-bi">&#x1F6E2;&#xFE0F;</div><div class="vm-bn">OIL</div>
            <div class="vm-bq">{{ order.oilLiters }} L</div><div class="vm-bs">&#10003; DISPENSED</div>
        </div>
        {% else %}
        <div class="vm-badge na">
            <div class="vm-bi">&#x1F6E2;&#xFE0F;</div><div class="vm-bn">OIL</div><div class="vm-bq">&#8212;</div><div class="vm-bs">N/A</div>
        </div>
        {% endif %}

        {% if order.soapCount > 0 and not order.soapDispensed %}
        <div class="vm-badge avail" onclick="dispense('soap','5')">
            <div class="vm-bi">&#x1F9FC;</div><div class="vm-bn">SOAP [5]</div>
            <div class="vm-bq">{{ order.soapCount }} pc</div><div class="vm-bs">&#9679; READY</div>
        </div>
        {% elif order.soapCount > 0 and order.soapDispensed %}
        <div class="vm-badge done">
            <div class="vm-bi">&#x1F9FC;</div><div class="vm-bn">SOAP</div>
            <div class="vm-bq">{{ order.soapCount }} pc</div><div class="vm-bs">&#10003; DISPENSED</div>
        </div>
        {% else %}
        <div class="vm-badge na">
            <div class="vm-bi">&#x1F9FC;</div><div class="vm-bn">SOAP</div><div class="vm-bq">&#8212;</div><div class="vm-bs">N/A</div>
        </div>
        {% endif %}

        {% if order.detergentCount > 0 and not order.detergentDispensed %}
        <div class="vm-badge avail" onclick="dispense('detergent','6')">
            <div class="vm-bi">&#x1FAE7;</div><div class="vm-bn">DETERGENT [6]</div>
            <div class="vm-bq">{{ order.detergentCount }} pc</div><div class="vm-bs">&#9679; READY</div>
        </div>
        {% elif order.detergentCount > 0 and order.detergentDispensed %}
        <div class="vm-badge done">
            <div class="vm-bi">&#x1FAE7;</div><div class="vm-bn">DETERGENT</div>
            <div class="vm-bq">{{ order.detergentCount }} pc</div><div class="vm-bs">&#10003; DISPENSED</div>
        </div>
        {% else %}
        <div class="vm-badge na">
            <div class="vm-bi">&#x1FAE7;</div><div class="vm-bn">DETERGENT</div><div class="vm-bq">&#8212;</div><div class="vm-bs">N/A</div>
        </div>
        {% endif %}
    </div>
'''
html = html.replace('    </div>\n\n    <div class="vm-keys">', badges_new + '\n    <div class="vm-keys">')

# 3. Keys
keys_old = '<button class="keypad-btn" {% if order.sugarKg == 0 or order.sugarDispensed %}disabled{% endif %} onclick="dispense(\'sugar\',\'3\')">3</button>'
keys_new = keys_old + '\n        <button class="keypad-btn" {% if order.oilLiters == 0 or order.oilDispensed %}disabled{% endif %} onclick="dispense(\'oil\',\'4\')">4</button>\n        <button class="keypad-btn" {% if order.soapCount == 0 or order.soapDispensed %}disabled{% endif %} onclick="dispense(\'soap\',\'5\')\">5</button>\n        <button class="keypad-btn" {% if order.detergentCount == 0 or order.detergentDispensed %}disabled{% endif %} onclick="dispense(\'detergent\',\'6\')\">6</button>'
html = html.replace(keys_old, keys_new)

# 4. JS window.VM
vm_old = '''window.VM = {
    av:  { rice: {{ 'true' if (order.riceKg > 0 and not order.riceDispensed) else 'false' }},
           wheat: {{ 'true' if (order.wheatKg > 0 and not order.wheatDispensed) else 'false' }},
           sugar: {{ 'true' if (order.sugarKg > 0 and not order.sugarDispensed) else 'false' }} },
    qty: { rice: {{ order.riceKg }}, wheat: {{ order.wheatKg }}, sugar: {{ order.sugarKg }} },
    dp:  { rice: {{ 'true' if order.riceDispensed else 'false' }}, wheat: {{ 'true' if order.wheatDispensed else 'false' }}, sugar: {{ 'true' if order.sugarDispensed else 'false' }} }
};'''
vm_new = '''window.VM = {
    av:  { rice: {{ 'true' if (order.riceKg > 0 and not order.riceDispensed) else 'false' }},
           wheat: {{ 'true' if (order.wheatKg > 0 and not order.wheatDispensed) else 'false' }},
           sugar: {{ 'true' if (order.sugarKg > 0 and not order.sugarDispensed) else 'false' }},
           oil: {{ 'true' if (order.oilLiters > 0 and not order.oilDispensed) else 'false' }},
           soap: {{ 'true' if (order.soapCount > 0 and not order.soapDispensed) else 'false' }},
           detergent: {{ 'true' if (order.detergentCount > 0 and not order.detergentDispensed) else 'false' }} },
    qty: { rice: {{ order.riceKg }}, wheat: {{ order.wheatKg }}, sugar: {{ order.sugarKg }}, oil: {{ order.oilLiters }}, soap: {{ order.soapCount }}, detergent: {{ order.detergentCount }} },
    dp:  { rice: {{ 'true' if order.riceDispensed else 'false' }}, wheat: {{ 'true' if order.wheatDispensed else 'false' }}, sugar: {{ 'true' if order.sugarDispensed else 'false' }}, oil: {{ 'true' if order.oilDispensed else 'false' }}, soap: {{ 'true' if order.soapDispensed else 'false' }}, detergent: {{ 'true' if order.detergentDispensed else 'false' }} }
};'''
html = html.replace(vm_old, vm_new)

# 5. JS maps
map_old1 = 'var keyMap = {\'1\':\'rice\',\'2\':\'wheat\',\'3\':\'sugar\'};'
map_new1 = 'var keyMap = {\'1\':\'rice\',\'2\':\'wheat\',\'3\':\'sugar\',\'4\':\'oil\',\'5\':\'soap\',\'6\':\'detergent\'};'
html = html.replace(map_old1, map_new1)

map_old2 = 'var labels  = {rice:\'Rice\',wheat:\'Wheat\',sugar:\'Sugar\'};'
map_new2 = 'var labels  = {rice:\'Rice\',wheat:\'Wheat\',sugar:\'Sugar\',oil:\'Oil\',soap:\'Soap\',detergent:\'Detergent\'};'
html = html.replace(map_old2, map_new2)

map_old3 = 'var icons   = {rice:\'&#x1F33E;\',wheat:\'&#x1F33F;\',sugar:\'&#x1F36C;\'};'
map_new3 = 'var icons   = {rice:\'&#x1F33E;\',wheat:\'&#x1F33F;\',sugar:\'&#x1F36C;\',oil:\'&#x1F6E2;&#xFE0F;\',soap:\'&#x1F9FC;\',detergent:\'&#x1FAE7;\'};'
html = html.replace(map_old3, map_new3)

# 6. ITM array and 3D logic
itm_old = '''var ITM = [
    {key:'rice',  label:'RICE',  slot:'1', hex:0xf9a825, emi:0x5a3c00, y: 0.44},
    {key:'wheat', label:'WHEAT', slot:'2', hex:0x7cb342, emi:0x2a4a10, y: 0.00},
    {key:'sugar', label:'SUGAR', slot:'3', hex:0xec407a, emi:0x6a0020, y:-0.44}
];'''
itm_new = '''var ITM = [
    {key:'rice',  label:'RICE',  slot:'1', hex:0xf9a825, emi:0x5a3c00, x: -0.32, y: 0.32},
    {key:'wheat', label:'WHEAT', slot:'2', hex:0x7cb342, emi:0x2a4a10, x:  0.32, y: 0.32},
    {key:'sugar', label:'SUGAR', slot:'3', hex:0xec407a, emi:0x6a0020, x: -0.32, y:-0.15},
    {key:'oil',   label:'OIL',   slot:'4', hex:0xffca28, emi:0x8a6c00, x:  0.32, y:-0.15},
    {key:'soap',  label:'SOAP',  slot:'5', hex:0x42a5f5, emi:0x004a80, x: -0.32, y:-0.62},
    {key:'detergent', label:'DETERG', slot:'6', hex:0xab47bc, emi:0x4a0060, x:  0.32, y:-0.62}
];'''
html = html.replace(itm_old, itm_new)

# Modify 3D slot placements
html = html.replace('put(mkBox(1.0,.38,.50', 'put(mkBox(0.6,.38,.50')
html = html.replace('0,it.y,ZS);', 'it.x,it.y,ZS);') # back wall
html = html.replace('put(mkBox(1.12,.014,.022', 'put(mkBox(1.22,.014,.022') # wider shelf

# Fix hopper x
html = html.replace('hop.position.set(0,it.y+.04,ZS);', 'hop.position.set(it.x,it.y+.04,ZS);')
html = html.replace('new THREE.BoxGeometry(.78,.22,.40)', 'new THREE.BoxGeometry(.48,.22,.40)') # smaller hopper

# Fix label plane
html = html.replace('lbl.position.set(.02,it.y,FZ+.015);', 'lbl.position.set(it.x+.02,it.y,FZ+.015);')
# LED dot
html = html.replace('put(mkBox(.034,.034,.016,lc2,.1,0,lc2,dp?.6:2.5),.54,it.y,FZ+.016);', 'put(mkBox(.034,.034,.016,lc2,.1,0,lc2,dp?.6:2.5),it.x+.24,it.y,FZ+.016);')
# Glow light
html = html.replace('gl.position.set(0,it.y,MD/2+.22);', 'gl.position.set(it.x,it.y,MD/2+.22);')

# Fix keypad
html = html.replace('var KY=-MH/2+.52;', 'var KY=-MH/2+.38;') # move keypad slightly down
html = html.replace('var xOff=it.key===\'rice\'?-.24:(it.key===\'wheat\'?0:.24);', 'var xOff=(parseInt(it.slot)-1)%3*0.22 - 0.22;\n    var yOff=KY - Math.floor((parseInt(it.slot)-1)/3)*0.22;')
html = html.replace('btn.position.set(xOff,KY,FZ+.015);', 'btn.position.set(xOff,yOff,FZ+.015);')
html = html.replace('bf.position.set(xo,KY,FZ+.032);', 'bf.position.set(xo,yOff,FZ+.032);')
# Fix RFID panel pos
html = html.replace('rl.position.set(.46,KY,FZ+.013);', 'rl.position.set(.46,KY-0.1,FZ+.013);')
html = html.replace('put(mkBox(.17,.24,.020,0x0a0f0a,.5,.6),.46,KY,FZ+.001);', 'put(mkBox(.17,.24,.020,0x0a0f0a,.5,.6),.46,KY-0.1,FZ+.001);')

# Fix collection tray
html = html.replace('put(mkBox(1.07,.08,.020,0x030305,.92,0),0,-MH/2+.33,FZ+.001);', 'put(mkBox(1.07,.08,.020,0x030305,.92,0),0,-MH/2+.15,FZ+.001);')
html = html.replace('put(mkBox(1.16,.06,.28,0x1a2529,.62,.72),0,-MH/2+.27,FZ+.12);', 'put(mkBox(1.16,.06,.28,0x1a2529,.62,.72),0,-MH/2+.09,FZ+.12);')
html = html.replace('put(mkBox(1.16,.10,.016,0x263238,.5,.8),0,-MH/2+.30,FZ+.248);', 'put(mkBox(1.16,.10,.016,0x263238,.5,.8),0,-MH/2+.12,FZ+.248);')
html = html.replace('tl.position.set(0,-MH/2+.30,FZ+.257);', 'tl.position.set(0,-MH/2+.12,FZ+.257);')

# Dispense animation target Y
html = html.replace('targetY:-MH/2+.31', 'targetY:-MH/2+.13')

with open('templates/vending-machine.html', 'w', encoding='utf-8') as f:
    f.write(html)
