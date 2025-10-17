#!/usr/bin/env python3
"""
🎃 Halloween RPG — A Mansão do Amuleto Sombrio
- Tema: Halloween (fantasmas, abóboras, bruxas, doces/truques)
- Features:
  * Classes Player/Enemy/Item
  * Inventário, equip, uso de itens
  * Eventos temáticos (trick-or-treat, enigma do espelho, caminho de abóboras)
  * Encontro com um boss final "Rei das Sombras"
  * Guardar/carregar progresso (JSON)
  * Sons simples (winsound no Windows, opcional)
  * Comentado para aprendizagem
  Emojis a usar - ✨ | 🎃 | 🍬 | 🎁 | ⚠️ | 😵 | 🔮 | 🔒 | 🕯️ 🍭 | 👻 | ⚔️ | ➡️ | ❗ | ☠️ | 🎉 | 🔔 | 🔆 | 🔕 | 🔎
"""
#Bibliotecas
import random
import json
import os
import time


SAVE_FILE = "halloween_save.json" # É o nome do ficheiro em que se vai começar o jogo.
if not os.path.exists(SAVE_FILE):   # Verifica se o nome do ficheiro existe.
    with open(SAVE_FILE, "w") as f: # Abre o ficheiro no modo de escrita ("w").
        json.dump({"pontuacao": 0, "nivel": 1}, f) # Escreve um dicionário com os dados iniciais no ficheiro.
        print("Ficheiro de save criado com sucesso!")   # Exibe uma mensagem no terminal indicando que o ficheiro de foi criado com sucesso.
else:
    print("Ficheiro de save já existe.")

#Ficheiro jason que tem que ser criado automaticamente falta o resto do código para criar auto

# winsound (Windows) para efeitos sonoros simples
try:
    import winsound
    # Função genérica para emitir um som simples
    def beep(freq=750, dur=150):
        winsound.Beep(freq, dur)
    # Função de som de recompensa (ex: apanhar moeda, ganhar ponto, etc.)
    def som_recompensa():
        frequencia = 880  # tom agudo tipo 'moeda'
        duracao = 200  # 0.2 segundos
        winsound.Beep(frequencia, duracao)
    # Função de som de erro (ex: falhar desafio, resposta errada)
    def som_erro():
        frequencia = 400  # tom mais grave
        duracao = 300
        winsound.Beep(frequencia, duracao)
except Exception:
    def beep(freq=750, dur=150):
        pass
    def som_recompensa():
        pass
    def som_erro():
        pass

    # -------------------------
    # Classes
    # -------------------------

class Item:
    def __init__(self, name, desc, heal=0, power=0, special=None):
        self.name = name
        self.desc = desc
        self.heal = heal
        self.power = power
        self.special = special

    def to_dict(self):
        return {"name": self.name, "desc": self.desc, "heal": self.heal, "power": self.power, "special": self.special}

    @staticmethod
    def from_dict(d):
        return Item(d["name"], d["desc"], d["heal"], d["power"], d.get("special"))


class Enemy:
    def __init__(self, name, hp, atk, xp, spooky_desc=""):
        self.name = name
        self.hp = hp
        self.atk = atk
        self.xp = xp
        self.spooky_desc = spooky_desc

    def is_dead(self):
        return self.hp <= 0


class Player:
    def __init__(self, name):
        self.name = name

    def attack_power(self):
        return self.base_atk + self.equipped_power

    def is_dead(self):
        return self.hp <= 0

    def heal(self, amt):
        old = self.hp
        self.hp = min(self.max_hp, self.hp + amt)
        return self.hp - old

    def add_item(self, item):
        if len(self.inventory) >= 7:
            return False
        self.inventory.append(item)
        return True

    def remove_item(self, idx):
        if 0 <= idx < len(self.inventory):
            return self.inventory.pop(idx)
        return None

    def gain_xp(self, amount):
        self.xp += amount
        leveled = False
        while self.xp >= 10 * self.level:
            self.xp -= 10 * self.level
            self.level += 1
            self.max_hp += 6
            self.base_atk += 1
            self.hp = self.max_hp
            leveled = True
            print(f"\n✨ Subiste nível! Agora és nível {self.level}. HP e ataque aumentaram.")
            beep(900, 120)
        return leveled

    def to_dict(self):
        return {
            "name": self.name, "max_hp": self.max_hp, "hp": self.hp, "base_atk": self.base_atk,
            "xp": self.xp, "level": self.level,
            "inventory": [i.to_dict() for i in self.inventory],
            "equipped_power": self.equipped_power, "candies": self.candies, "scare_meter": self.scare_meter
        }
# -------------------------
# Conteúdo temático
# -------------------------
ALL_ITEMS = [
    Item("Poção de Lua", "Cura 10 HP.", heal=10),
    Item("Doce Mágico", "Cura 25 HP.", heal=25),
    Item("Adaga de Osso", "Cura 5 HP.", heal=5),
    Item("Amuleto Abóbora", "Cura 15 HP.", heal=15),
    Item("Velha Vela", "Cura 2 HP.", heal=2),
]

ENEMIES = [
    Enemy("Gato das Sombras", 12, 3, 3, "um gato cujos olhos brilham como brasas"),
    Enemy("Bruxa Errante", 30 , 5 , 5 , "uma bruxa que berra as poções"),
    Enemy("Espectro Fedorento", 20 , 8 , 15,"um espectro que cheira pior que queijo podre \n e da vomitos com aquele cheiro"),
    Enemy("Cavaleiro Cadavérico", 50 ,10 , 20 , "este cavaleiro é o mais forte do reino e \n está pronto para derrotar qualquer um...")
#estes são os inimigos existentes
]

BOSS = Enemy("Rei das Sombras", 45, 9, 20, "o Senhor das Trevas da Mansão")

# -------------------------
# Utilitários
# -------------------------
#Este código a baixo tem que ser todo documentado
def clear():
    os.system('cls' if os.name == 'nt' else 'clear')

def pause(sec=0.9):
    time.sleep(sec)

def choose(prompt, options):
    options = [o.lower() for o in options]
    while True:
        r = input(prompt).strip().lower()
        if r in options:
            return r
        print("Opção inválida, tenta de novo.")

def save_game(player, room, has_amuleto):
    data = {"player": player.to_dict(), "room": room, "has_amuleto": has_amuleto}
    with open(SAVE_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    print("💾 Jogo guardado.")

def load_game():
    if not os.path.exists(SAVE_FILE):
        return None
    with open(SAVE_FILE, "r", encoding="utf-8") as f:
        data = json.load(f)
    return Player.from_dict(data["player"]), data.get("room", 0), data.get("has_amuleto", False)

# -------------------------
# Eventos de Halloween
# -------------------------
def trick_or_treat(player):
    """Evento: bater em portas, ganhar doces ou armadilhas."""
    print("\n🎃 Entras numa sala com portas decoradas. É noite de trick-or-treat!")
    roll = random.random()
    if roll < 0.5:
        print("Não encontraste nada abre mais uma porta e surpreende-te!")
        #por programar
    elif roll < 0.8:
        item = random.choice(ALL_ITEMS)
        print(f"🎁 Encontraste um item: {item.name} - {item.desc}")
        if player.add_item(item):
            print("Item guardado no inventário.")
        else:
            print("Inventário cheio — deixas o item no chão.")
        return True
    else:
        # armadilha: perde vida ou aumenta scare em random
        player.scare_meter += 2
        print("⚠️ Era uma pegadinha! Ficas assustado e o scare meter aumenta.")
    # Resto código com if
        return True

def haunted_mirror(player):
    """Enigma de espelho — reorganizar letras (tema: SPOOKY)"""
    secret = "SPOOKY"
    scrambled = "".join(random.sample(list(secret), len(secret)))
    print("\n🔮 Um espelho emite um brilho — aparece um enigma nas letras:")
    print(f"Letras: {scrambled}")
    ans = input("Escreve a palavra correta: ").strip().upper()
    if ans == secret:
        print("✨ O espelho sorri! Ganha-se 4 doces e um item mágico.")
        player.candies += 4
        item = Item("Runas da Noite", "Item mágico: aumenta ataque +2.", power=2)
        player.add_item(item)
        beep(1000, 120)
        return True
    else:
        print("🔒 O espelho silencia. O scare meter sobe.")
        player.scare_meter += 1
        return False
#se acertar a palavra return true e ganha-se dois de poder, caso errar return false e tira-se 1 de poder
def pumpkin_path(player):
    """Caminho de abóboras — risco/benefício."""
    print("\n🕯️ Segues um caminho de abóboras iluminadas...")
    choice = choose("Queres seguir o caminho arriscado por mais doces? (s/n): ", ["s","n"])
    if choice == "s":
        if random.random() < 0.5:
            gained = random.randint(2,4)
            print(f"🍭 Achaste um saco de doces: +{gained} doces!")
            player.candies += gained
            beep(820, 100)
            return True
        else:
            lost = random.randint(1,4)
            player.hp -= lost
            player.scare_meter += 1
            print(f"👻 Era uma rampa oculta! Perdes {lost} HP e o scare meter aumenta.")
            return True
    else:
        print("Segues cautelosamente e nada acontece.")
        return True

def ghost_encounter(player):
    print("\n👻 Um fantasma sussurra na tua orelha...")
    choice = choose("O que fazes? (falar/oferecer/fugir): ", ["falar","oferecer","fugir"])
    if choice == "falar":
        print("O fantasma não quer falar contigo e ataca-te")
        dmg = enemy.atk + random.randint(1, 5)
        return True
    if choice == "oferecer":
        print("Obrigado pelos doces, pra próxima veremos se será suficiente...")
        lost = random.randint(1, 4)
        player.candies -= lost
        return True
    else:
        print("Tentas fugir mas o fantasme ataca-te e perdes poder de ataque.")
        lost = random.randint(1, 5)
        player.attack_power -= lost
        return True
    #Mesma lógica do código a cima mas com 3 opções

# -------------------------
# Combate adaptado
# -------------------------
#Este parte do código está mal formatado porquê?

def combat(player, enemy):
        print(f"\n⚔️ Enfrentas: {enemy.name} — {enemy.spooky_desc} (HP {enemy.hp})")
        while not enemy.is_dead() and not player.is_dead():
            print(
                f"\nTeu HP: {player.hp}/{player.max_hp}  |  Ataque: {player.attack_power()}  |  Candies: {player.candies}  |  Scare: {player.scare_meter}")
            print("Opções: (a) Atacar  (u) Usar item  (f) Fugir")
            cmd = choose("> ", ["a", "u", "f"])
            if cmd == "a":
                dmg = player.attack_power() + random.randint(0, 3)
                enemy.hp -= dmg
                print(f"➡️ Atacas e causas {dmg} de dano.")
                beep(700, 80)
                # Mesma lógica do código a cima mas com 3 opções
            elif cmd == "u":
                if not player.inventory:
                    print("Inventário vazio.")
                else:
                    for idx, it in enumerate(player.inventory):
                            print(f"{idx + 1}. {it.name} — {it.desc}")
                        sel = input("Escolhe número do item (ou ENTER): ").strip()
                    if sel.isdigit():
                        i = int(sel) - 1
                        if 0 <= i < len(player.inventory):
                            it = player.remove_item(i)
                            if it.heal:
                                healed = player.heal(it.heal)
                                print(f"Usaste {it.name} e curaste {healed} HP.")
                            if it.power:
                                player.equipped_power += it.power
                                print(f"Equippaste {it.name}: +{it.power} ataque.")
                            if it.special == "candy_boost":
                                player.candies += 2
                                print("O doce mágico aumenta os teus candies em +2!")
                            if it.special == "calm":
                                player.scare_meter = max(0, player.scare_meter - 1)
                                print("A vela acalma-te: scare meter -1.")
                        else:
                                print("Índice inválido.")
                    else:
                        print("Cancelado.")
            else:  # fugir
                if random.random() < 0.5:
                    print("Fugiste com sucesso!")
                    return False
                else:
                    print("Tentativa falhou!")
                    # inimigo ataca
                    if not enemy.is_dead():
                        dmg = enemy.atk + random.randint(0, 2)
                        player.hp -= dmg
                        print(f"❗ {enemy.name} contra-ataca e causa {dmg} de dano.")
                        if random.random() < 0.2:
                            player.scare_meter += 1
                            print("O encontro aumenta o teu scare meter (+1).")
                            if player.is_dead():
                                print("☠️ Foste derrotado na Mansão...")
                                return False
                            else:
                                print(f"🎉 Derrubaste {enemy.name} e ganhaste {enemy.xp} XP!")
                                player.gain_xp(enemy.xp)
                                # recompensa em doces
                                candies = random.randint(1, 3)
                                player.candies += candies
                                print(f"Recebes {candies} doces extras. Total candies: {player.candies}")
                                return True
        #Comentar todo o código a cima

#O resto do código vai ser passado na próxima aula falta +- 300 linhas de código :):)
# -------------------------
# Enigma final (tema do amuleto sombrio)
# -------------------------