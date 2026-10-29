"""Build the word data embedded in games/trivoca.html (Trivoca Kids).

Answers are the hand-picked kid words below (ages ~8-9), each with an emoji
and a category used by the first hint. Accepted guesses are much broader so
kids rarely see "not a word": the answers, plus common 4- and 5-letter words
from wordfreq, plus whatever accepted 5-letter words the page already has.

    pip install wordfreq
    python3 tools/trivoca_kids_words.py

Re-running is safe: it rewrites the <script id="words"> block in place.
"""
import json
import re
import sys
import unicodedata
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
PAGE = ROOT / "games" / "trivoca.html"
LENGTHS = (4, 5)

# Category codes; the labels live in the page (T[lang].cats).
CATS = {"an", "fo", "na", "sk", "ho", "bo", "sc", "pl", "mu", "cl", "tr", "pe", "co"}

# word emoji category — one per line, accents as they should be shown.
KIDS = {
"en": """
bear 🐻 an
bird 🐦 an
frog 🐸 an
fish 🐟 an
duck 🦆 an
goat 🐐 an
lion 🦁 an
wolf 🐺 an
deer 🦌 an
crab 🦀 an
seal 🦭 an
swan 🦢 an
lamb 🐑 an
bull 🐂 an
hare 🐇 an
worm 🪱 an
dove 🕊️ an
pony 🐴 an
slug 🐌 an
toad 🐸 an
mole 🐾 an
horse 🐴 an
tiger 🐯 an
zebra 🦓 an
sheep 🐑 an
shark 🦈 an
whale 🐳 an
snake 🐍 an
mouse 🐭 an
camel 🐫 an
panda 🐼 an
koala 🐨 an
eagle 🦅 an
otter 🦦 an
llama 🦙 an
sloth 🦥 an
skunk 🦨 an
moose 🫎 an
goose 🪿 an
bunny 🐰 an
puppy 🐶 an
kitty 🐱 an
chick 🐤 an
hippo 🦛 an
rhino 🦏 an
squid 🦑 an
snail 🐌 an
robin 🐦 an
gecko 🦎 an
bison 🦬 an
cake 🎂 fo
milk 🥛 fo
rice 🍚 fo
corn 🌽 fo
pear 🍐 fo
soup 🍲 fo
meat 🍖 fo
bean 🫘 fo
taco 🌮 fo
kiwi 🥝 fo
salt 🧂 fo
lime 🍋 fo
beef 🥩 fo
chip 🍟 fo
mint 🌿 fo
food 🍽️ fo
apple 🍎 fo
bread 🍞 fo
lemon 🍋 fo
mango 🥭 fo
melon 🍈 fo
pizza 🍕 fo
pasta 🍝 fo
salad 🥗 fo
honey 🍯 fo
juice 🧃 fo
grape 🍇 fo
peach 🍑 fo
bacon 🥓 fo
candy 🍬 fo
toast 🍞 fo
olive 🫒 fo
onion 🧅 fo
sushi 🍣 fo
donut 🍩 fo
fruit 🍓 fo
water 💧 fo
chili 🌶️ fo
curry 🍛 fo
bagel 🥯 fo
berry 🫐 fo
snack 🍿 fo
lunch 🥪 fo
tree 🌳 na
leaf 🍃 na
rock 🪨 na
sand 🏖️ na
lake 🏞️ na
hill ⛰️ na
seed 🌱 na
rose 🌹 na
wave 🌊 na
fire 🔥 na
palm 🌴 na
pine 🌲 na
reef 🪸 na
plant 🪴 na
grass 🌱 na
river 🏞️ na
beach 🏖️ na
ocean 🌊 na
stone 🪨 na
tulip 🌷 na
daisy 🌼 na
lotus 🪷 na
shell 🐚 na
coral 🪸 na
field 🌾 na
woods 🌲 na
earth 🌍 na
acorn 🌰 na
moon 🌙 sk
star ⭐ sk
rain 🌧️ sk
snow ❄️ sk
wind 💨 sk
cloud ☁️ sk
storm ⛈️ sk
comet ☄️ sk
sunny ☀️ sk
door 🚪 ho
lamp 💡 ho
sofa 🛋️ ho
bath 🛁 ho
sink 🚰 ho
soap 🧼 ho
fork 🍴 ho
bowl 🥣 ho
dish 🍽️ ho
bell 🔔 ho
roof 🏠 ho
wall 🧱 ho
home 🏡 ho
room 🛏️ ho
vase 🏺 ho
rope 🪢 ho
chair 🪑 ho
clock ⏰ ho
couch 🛋️ ho
spoon 🥄 ho
knife 🔪 ho
plate 🍽️ ho
glass 🥛 ho
house 🏠 ho
broom 🧹 ho
bench 🪑 ho
radio 📻 ho
phone 📱 ho
hand ✋ bo
foot 🦶 bo
nose 👃 bo
hair 💇 bo
face 😊 bo
lips 👄 bo
bone 🦴 bo
nail 💅 bo
eyes 👀 bo
ears 👂 bo
legs 🦵 bo
heart ❤️ bo
tooth 🦷 bo
brain 🧠 bo
mouth 👄 bo
thumb 👍 bo
smile 😁 bo
book 📖 sc
desk 🪑 sc
math ➗ sc
test 📝 sc
note 🗒️ sc
page 📄 sc
word 🔤 sc
quiz ❓ sc
clip 📎 sc
paper 📄 sc
ruler 📏 sc
class 🏫 sc
globe 🌍 sc
books 📚 sc
ball ⚽ pl
kite 🪁 pl
game 🎮 pl
doll 🪆 pl
golf ⛳ pl
goal 🥅 pl
race 🏁 pl
team 👥 pl
yoyo 🪀 pl
card 🃏 pl
dice 🎲 pl
surf 🏄 pl
judo 🥋 pl
sled 🛷 pl
tent ⛺ pl
park 🏞️ pl
robot 🤖 pl
dance 💃 pl
block 🧱 pl
chess ♟️ pl
skate ⛸️ pl
medal 🏅 pl
cards 🃏 pl
magic 🪄 pl
party 🥳 pl
drum 🥁 mu
song 🎵 mu
horn 📯 mu
harp 🎼 mu
piano 🎹 mu
flute 🪈 mu
drums 🥁 mu
banjo 🪕 mu
music 🎶 mu
shoe 👟 cl
coat 🧥 cl
sock 🧦 cl
boot 👢 cl
cape 🦸 cl
ring 💍 cl
mask 🎭 cl
gown 👗 cl
vest 🦺 cl
tutu 🩰 cl
dress 👗 cl
shirt 👕 cl
jeans 👖 cl
scarf 🧣 cl
boots 👢 cl
shoes 👟 cl
socks 🧦 cl
crown 👑 cl
glove 🧤 cl
boat ⛵ tr
ship 🚢 tr
bike 🚲 tr
taxi 🚕 tr
tram 🚋 tr
road 🛣️ tr
city 🏙️ tr
town 🏘️ tr
farm 🚜 tr
shop 🏪 tr
train 🚆 tr
plane ✈️ tr
truck 🚚 tr
wheel 🛞 tr
ferry ⛴️ tr
canoe 🛶 tr
yacht ⛵ tr
hotel 🏨 tr
tower 🗼 tr
store 🏪 tr
baby 👶 pe
king 🤴 pe
girl 👧 pe
lady 👩 pe
chef 🧑‍🍳 pe
hero 🦸 pe
twin 👯 pe
queen 👸 pe
pilot 🧑‍✈️ pe
nurse 🧑‍⚕️ pe
clown 🤡 pe
fairy 🧚 pe
ghost 👻 pe
witch 🧙 pe
baker 🧁 pe
child 🧒 pe
ninja 🥷 pe
giant 🦶 pe
blue 🔵 co
pink 🩷 co
gold 🟡 co
gray 🩶 co
green 🟢 co
black ⚫ co
white ⚪ co
brown 🟤 co
""",
"es": """
sapo 🐸 an
reno 🦌 an
mula 🫏 an
cerdo 🐷 an
yegua 🐴 an
ostra 🦪 an
nido 🪺 na
pasto 🌱 na
campo 🌾 na
pluma 🪶 na
perla 🦪 na
nuez 🌰 fo
lupa 🔍 sc
ropa 👕 cl
hilo 🧵 cl
sala 🛋️ ho
ojos 👀 bo
pies 🦶 bo
remo 🚣 pl
bola ⚽ pl
tenis 🎾 pl
feria 🎡 pl
circo 🎪 pl
disco 💿 mu
yate ⛵ tr
canoa 🛶 tr
torre 🗼 tr
banco 🏦 tr
hijo 👦 pe
hija 👧 pe
gato 🐱 an
pato 🦆 an
lobo 🐺 an
león 🦁 an
vaca 🐄 an
rana 🐸 an
mono 🐵 an
foca 🦭 an
pavo 🦃 an
toro 🐂 an
loro 🦜 an
búho 🦉 an
alce 🫎 an
orca 🐋 an
puma 🐆 an
oveja 🐑 an
pollo 🐔 an
erizo 🦔 an
cisne 🦢 an
tigre 🐯 an
burro 🫏 an
zorro 🦊 an
perro 🐶 an
ratón 🐭 an
cebra 🦓 an
koala 🐨 an
panda 🐼 an
gallo 🐓 an
abeja 🐝 an
mosca 🪰 an
pulpo 🐙 an
cabra 🐐 an
llama 🦙 an
pera 🍐 fo
sopa 🍲 fo
miel 🍯 fo
taco 🌮 fo
uvas 🍇 fo
kiwi 🥝 fo
piña 🍍 fo
coco 🥥 fo
maíz 🌽 fo
jugo 🧃 fo
flan 🍮 fo
lima 🍋 fo
atún 🐟 fo
cena 🍽️ fo
arroz 🍚 fo
leche 🥛 fo
pizza 🍕 fo
queso 🧀 fo
carne 🍖 fo
huevo 🥚 fo
tarta 🥧 fo
dulce 🍬 fo
melón 🍈 fo
mango 🥭 fo
limón 🍋 fo
fresa 🍓 fo
pasta 🍝 fo
torta 🎂 fo
fruta 🍎 fo
salsa 🥫 fo
flor 🌸 na
hoja 🍃 na
lago 🏞️ na
isla 🏝️ na
roca 🪨 na
rosa 🌹 na
pino 🌲 na
agua 💧 na
lodo 🟫 na
árbol 🌳 na
nieve ⛄ na
playa 🏖️ na
monte ⛰️ na
selva 🌴 na
arena 🏜️ na
fuego 🔥 na
hielo 🧊 na
trigo 🌾 na
nube ☁️ sk
luna 🌙 sk
rayo ⚡ sk
aire 💨 sk
cielo 🌤️ sk
casa 🏠 ho
mesa 🍽️ ho
cama 🛏️ ho
sofá 🛋️ ho
vaso 🥛 ho
taza ☕ ho
baño 🛁 ho
vela 🕯️ ho
olla 🍲 ho
caja 📦 ho
foto 📷 ho
cubo 🪣 ho
silla 🪑 ho
plato 🍽️ ho
llave 🔑 ho
techo 🏠 ho
jabón 🧼 ho
reloj ⏰ ho
bolsa 👜 ho
radio 📻 ho
peine 🪮 ho
mano ✋ bo
pelo 💇 bo
boca 👄 bo
dedo ☝️ bo
codo 💪 bo
cara 😊 bo
piel 🖐️ bo
nariz 👃 bo
brazo 💪 bo
oreja 👂 bo
labio 👄 bo
hueso 🦴 bo
panza 🤰 bo
barba 🧔 bo
mapa 🗺️ sc
nota 📝 sc
aula 🏫 sc
arte 🎨 sc
idea 💡 sc
suma ➕ sc
lápiz ✏️ sc
libro 📖 sc
clase 🏫 sc
regla 📏 sc
papel 📄 sc
letra 🔤 sc
resta ➖ sc
dado 🎲 pl
golf ⛳ pl
judo 🥋 pl
surf 🏄 pl
yoyó 🪀 pl
meta 🏁 pl
juego 🎮 pl
globo 🎈 pl
carta 🃏 pl
patín ⛸️ pl
robot 🤖 pl
magia 🪄 pl
baile 💃 pl
esquí ⛷️ pl
arpa 🎼 mu
piano 🎹 mu
banda 🎺 mu
canto 🎤 mu
bota 👢 cl
capa 🦸 cl
tutú 🩰 cl
gorra 🧢 cl
traje 🤵 cl
falda 👗 cl
gafas 🕶️ cl
casco ⛑️ cl
botas 👢 cl
tren 🚆 tr
auto 🚗 tr
moto 🏍️ tr
taxi 🚕 tr
bici 🚲 tr
ruta 🛣️ tr
cine 🎬 tr
nave 🚀 tr
barco ⛵ tr
avión ✈️ tr
coche 🚗 tr
calle 🛣️ tr
hotel 🏨 tr
museo 🏛️ tr
ancla ⚓ tr
bebé 👶 pe
niño 🧒 pe
niña 👧 pe
papá 👨 pe
mamá 👩 pe
hada 🧚 pe
mago 🧙 pe
chef 🧑‍🍳 pe
reina 👸 pe
amigo 🤝 pe
bruja 🧙 pe
héroe 🦸 pe
ninja 🥷 pe
rojo 🔴 co
azul 🔵 co
gris 🩶 co
lila 🟣 co
verde 🟢 co
negro ⚫ co
""",
"pt": """
mico 🐒 an
boto 🐬 an
mula 🫏 an
siri 🦀 an
égua 🐴 an
cisne 🦢 an
lebre 🐇 an
grilo 🦗 an
ninho 🪺 na
pena 🪶 na
lama 🟫 na
campo 🌾 na
uvas 🍇 fo
ovos 🥚 fo
açaí 🫐 fo
nozes 🌰 fo
lupa 🔍 sc
pasta 📁 sc
sala 🛋️ ho
vaso 🏺 ho
lixo 🗑️ ho
cesta 🧺 ho
fita 🎀 cl
laço 🎀 cl
roupa 👕 cl
remo 🚣 pl
rede 🥅 pl
iate ⛵ tr
canoa 🛶 tr
praça 🏞️ tr
torre 🗼 tr
banco 🏦 tr
disco 💿 mu
filha 👧 pe
gato 🐱 an
pato 🦆 an
lobo 🐺 an
leão 🦁 an
vaca 🐄 an
sapo 🐸 an
rato 🐭 an
urso 🐻 an
foca 🦭 an
peru 🦃 an
galo 🐓 an
onça 🐆 an
lula 🦑 an
orca 🐋 an
alce 🫎 an
puma 🐆 an
tigre 🐯 an
zebra 🦓 an
cobra 🐍 an
pavão 🦚 an
peixe 🐟 an
polvo 🐙 an
burro 🫏 an
porco 🐷 an
panda 🐼 an
coala 🐨 an
arara 🦜 an
touro 🐂 an
veado 🦌 an
lhama 🦙 an
ganso 🪿 an
águia 🦅 an
pombo 🕊️ an
pera 🍐 fo
sopa 🍲 fo
bolo 🎂 fo
kiwi 🥝 fo
coco 🥥 fo
suco 🧃 fo
doce 🍬 fo
maçã 🍎 fo
bala 🍬 fo
café ☕ fo
arroz 🍚 fo
leite 🥛 fo
milho 🌽 fo
pizza 🍕 fo
carne 🍖 fo
limão 🍋 fo
manga 🥭 fo
melão 🍈 fo
torta 🥧 fo
pudim 🍮 fo
fruta 🍓 fo
trigo 🌾 fo
flor 🌸 na
lago 🏞️ na
ilha 🏝️ na
rosa 🌹 na
onda 🌊 na
fogo 🔥 na
mata 🌳 na
gelo 🧊 na
água 💧 na
folha 🍃 na
pedra 🪨 na
praia 🏖️ na
areia 🏜️ na
terra 🌍 na
grama 🌱 na
neve ❄️ sk
raio ⚡ sk
nuvem ☁️ sk
chuva 🌧️ sk
vento 💨 sk
casa 🏠 ho
mesa 🍽️ ho
cama 🛏️ ho
sofá 🛋️ ho
copo 🥛 ho
vela 🕯️ ho
faca 🔪 ho
sino 🔔 ho
foto 📷 ho
teto 🏠 ho
prato 🍽️ ho
chave 🔑 ho
porta 🚪 ho
caixa 📦 ho
garfo 🍴 ho
rádio 📻 ho
sabão 🧼 ho
balde 🪣 ho
pente 🪮 ho
boca 👄 bo
olho 👁️ bo
dedo ☝️ bo
unha 💅 bo
osso 🦴 bo
cara 😊 bo
pele 🖐️ bo
nariz 👃 bo
dente 🦷 bo
braço 💪 bo
perna 🦵 bo
rosto 😊 bo
mapa 🗺️ sc
nota 📝 sc
aula 🏫 sc
arte 🎨 sc
lápis ✏️ sc
livro 📖 sc
papel 📄 sc
tinta 🖋️ sc
letra 🔤 sc
régua 📏 sc
ideia 💡 sc
conta ➕ sc
prova 📝 sc
bola ⚽ pl
jogo 🎮 pl
dado 🎲 pl
pipa 🪁 pl
robô 🤖 pl
judô 🥋 pl
time 👥 pl
balão 🎈 pl
carta 🃏 pl
festa 🥳 pl
dança 💃 pl
golfe ⛳ pl
surfe 🏄 pl
circo 🎪 pl
piano 🎹 mu
harpa 🎼 mu
samba 💃 mu
banda 🎺 mu
canto 🎤 mu
saia 👗 cl
bota 👢 cl
capa 🦸 cl
meia 🧦 cl
luva 🧤 cl
anel 💍 cl
boné 🧢 cl
coroa 👑 cl
blusa 👚 cl
calça 👖 cl
tênis 👟 cl
trem 🚆 tr
moto 🏍️ tr
táxi 🚕 tr
loja 🏪 tr
nave 🚀 tr
carro 🚗 tr
barco ⛵ tr
avião ✈️ tr
navio 🚢 tr
ponte 🌉 tr
hotel 🏨 tr
museu 🏛️ tr
farol 🗼 tr
bebê 👶 pe
vovó 👵 pe
fada 🧚 pe
mago 🧙 pe
papai 👨 pe
mamãe 👩 pe
amigo 🤝 pe
bruxa 🧙 pe
herói 🦸 pe
ninja 🥷 pe
filho 👦 pe
irmão 👦 pe
azul 🔵 co
roxo 🟣 co
verde 🟢 co
preto ⚫ co
cinza 🩶 co
lilás 🟣 co
""",
}


def key(word, lang):
    """Typed form: lowercase, accents and cedilla dropped (Spanish keeps ñ)."""
    out = []
    for ch in word.lower():
        if lang == "es" and ch == "ñ":
            out.append(ch)
            continue
        base = unicodedata.normalize("NFD", ch)[0]
        out.append(base)
    k = "".join(out)
    return k if re.fullmatch(r"[a-zñ]+", k) else None


def main():
    from wordfreq import top_n_list

    html = PAGE.read_text(encoding="utf-8")
    m = re.search(r'(<script id="words" type="application/json">)(.*?)(</script>)', html, re.S)
    old = json.loads(m.group(2))
    data, problems = {}, []

    for lang, text in KIDS.items():
        data[lang] = {str(L): {"a": [], "h": {}, "v": set(), "d": {}} for L in LENGTHS}
        # Accepted guesses: what the page already accepts, then common words.
        for L in LENGTHS:
            prev = old.get(lang, {}).get(str(L))
            if prev:
                data[lang][str(L)]["v"].update(prev["v"].split())
                data[lang][str(L)]["d"].update(prev.get("d", {}))
        for w in top_n_list(lang, 200000):
            k = key(w, lang)
            if not k or len(k) not in LENGTHS:
                continue
            bucket = data[lang][str(len(k))]
            bucket["v"].add(k)
            if w != k and k not in bucket["d"]:
                bucket["d"][k] = w
        # Answers, with their hint.
        seen = set()
        for line in text.strip().splitlines():
            parts = line.split()
            if len(parts) != 3:
                problems.append(f"{lang}: bad line {line!r}")
                continue
            word, emoji, cat = parts
            k = key(word, lang)
            if cat not in CATS:
                problems.append(f"{lang}: unknown category in {line!r}")
            if not k or len(k) not in LENGTHS:
                problems.append(f"{lang}: {word} is not {' or '.join(map(str, LENGTHS))} letters")
                continue
            if k in seen:
                problems.append(f"{lang}: duplicate {word}")
                continue
            seen.add(k)
            bucket = data[lang][str(len(k))]
            bucket["a"].append(k)
            bucket["h"][k] = [emoji, cat]
            bucket["v"].add(k)
            if word != k:
                bucket["d"][k] = word  # the answer's own spelling wins
            elif k in bucket["d"]:
                del bucket["d"][k]

    if problems:
        sys.exit("\n".join(problems))

    out = {}
    for lang in data:
        out[lang] = {}
        for L, b in data[lang].items():
            out[lang][L] = {"a": " ".join(b["a"]), "h": b["h"], "v": " ".join(sorted(b["v"])), "d": b["d"]}
            print(f"{lang} {L}: {len(b['a'])} answers, {len(b['v'])} accepted guesses")
    blob = json.dumps(out, ensure_ascii=False, separators=(",", ":"))
    PAGE.write_text(html[:m.start(2)] + blob + html[m.end(2):], encoding="utf-8")


if __name__ == "__main__":
    main()
