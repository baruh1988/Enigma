from itertools import permutations

alphabet = 'ABCDEFGHIJKLMNOPQRSTUVWXYZ'
alphabetDict = {x: alphabet.index(x) for x in alphabet}

# Historically accurate rotors according to https://en.wikipedia.org/wiki/Enigma_rotor_details
rotorCollection = {'I': 'EKMFLGDQVZNTOWYHXUSPAIBRCJ',
                   'II': 'AJDKSIRUXBLHWTMCQGZNPYFVOE',
                   'III': 'BDFHJLCPRTXVZNYEIWGAKMUSQO',
                   'IV': 'ESOVPZJAYQUIRHXLNFTGKDCMWB',
                   'V': 'VZBRGITYUPSDNHLXAWMJQOFECK',
                   'VI': 'JPGVOUMFYQBENHZRDKASXLICTW',
                   'VII': 'NZJHGRCXMYSWBOUFAIVLPEKQDT',
                   'VIII': 'FKQHTLXOCBJSPDZRAMEWNIUYGV'}

# Reflectors used to ensure no character encrypts to itself
# Historically accurate reflectors according to https://en.wikipedia.org/wiki/Enigma_rotor_details
reflectorCollection = {'A': 'EJMZALYXVBWFCRQUONTSPIKHGD',
                       'B': 'YRUHQSLDPXNGOKMIEBFZCWVJAT',
                       'C': 'FVPJIAOYEDRZXWGCTKUQSBNMHL',
                       'Bt': 'ENKQAUYWJICOPBLMDXZVFTHRGS',
                       'Ct': 'RDOBJNTKVEHMLFCWZAXGYIPSUQ'}

'''
Receives a string and returns a string that contains only letters from the original string in uppercase
'''


def RemoveChars(text):
    text = ''.join(text.upper().split())
    for _ in set((chr(x) for x in range(127))).difference(set(alphabet)):
        text = text.replace(_, '')
    return text


'''
Simulation of an Enigma machine. Receives a string, 3 rotors, a reflector and the offset of the rotors and returns an
encrypted string. Using the same settings on the encrypted string will decrypt it. No plug board implementation for
simplicity.

text: string to encrypt
rotors: a list of rotors from rotorCollection. Each rotor is represented by a roman numeral.
reflector: a reflector from reflectorCollection. Represented by a string
offset: a string of 3 letters representing the starting positions of each rotor
'''


def Enigma(text, rotors, reflector, offset):
    # Convert the original text to contain only uppercase letters
    text = RemoveChars(text)
    # Convert each rotor and the reflector to a list of letters
    rotors = [list(rotorCollection[x]) for x in rotors]
    reflector = list(reflectorCollection[reflector])
    # Counters to keep track of rotor rotations
    count = [rotors[i].index(offset[i]) % 26 for i in range(len(offset))]
    res = ''

    # Receives a rotor and rotates it by one step
    def RotateRotor(rotor):
        rotor.append(rotor.pop(0))

    # Sets the rotors to their starting position based on the offset
    def SetRotors():
        for i in range(len(count)):
            for j in range(count[i]):
                RotateRotor(rotors[i])

    # Encrypts a character by running it through each rotor, then the reflector and back through the rotors
    def EncryptCharacter(c):
        c = alphabetDict[c]
        # pass through first rotor
        c = rotors[0][c]
        c = alphabetDict[c]
        # pass through second rotor
        c = rotors[1][c]
        c = alphabetDict[c]
        # pass through third rotor
        c = rotors[2][c]
        c = alphabetDict[c]
        # pass through reflector
        c = reflector[c]
        # pass back through third rotor
        c = rotors[2].index(c)
        c = alphabet[c]
        # pass back through second rotor
        c = rotors[1].index(c)
        c = alphabet[c]
        # pass back through first rotor
        c = rotors[0].index(c)
        return alphabet[c]

    SetRotors()
    for t in text:
        res += EncryptCharacter(t)
        # First rotor rotates every character
        RotateRotor(rotors[0])
        count[0] += 1
        # Second rotor rotates once the first rotor completes a full cycle
        if count[0] % 26 == 0:
            RotateRotor(rotors[1])
            count[1] += 1
            # Third rotor rotates once the second rotor completes a full cycle
            if count[1] % 26 == 0:
                RotateRotor(rotors[2])

    return res


'''
Receives an encrypted string and a word. Checks every possible setting for the Enigma machine by decrypting the string
and checking if the the word is in the decrypted string. Return a list of possible settings. Takes some time to
complete, according to how many rotors and reflectors are in rotorCollection and reflectorCollection

text: encrypted string
guess: a word that is believed to be in the decrypted string
'''


def Bombe(text, guess):
    # Convert to contain only uppercase letters
    text, guess = RemoveChars(text), RemoveChars(guess)
    res = []
    print('Checking possible machine configurations. This may take a while!')
    try:
        # Iterate rotor combinations of 3 rotors from 8
        for combo in permutations(list(rotorCollection.keys()), 3):
            # Iterate reflectors
            for r in reflectorCollection.keys():
                # Iterate rotor offsets
                for offset1 in alphabet:
                    for offset2 in alphabet:
                        for offset3 in alphabet:
                            # Check if the word is in the text
                            if guess in Enigma(text, combo, r, offset1 + offset2 + offset3):
                                print({'rotors': combo, 'reflector': r, 'offset': offset1 + offset2 + offset3})
                                res.append({'rotors': combo, 'reflector': r, 'offset': offset1 + offset2 + offset3})
    except BaseException as err:
        print(err, '\nOperation terminated!')
    return res


def Main():
    menu = '''
    Choose option:
    1. Enigma (Encrypt/Decrypt)
    2. Bombe (Find encryption settings)
    3. Exit
    '''

    def SimEnigma():
        rotors = []
        reflector = ''
        offset = ''
        tmp = list(rotorCollection.keys())
        for i in range(3):
            print('Choose rotor:')
            for j in range(len(tmp)):
                print(str(j + 1) + ': ' + tmp[j])
            try:
                choice = int(input('Your choice: '))
                if not 1 <= choice <= len(tmp):
                    raise Exception('Invalid choice! ')
            except Exception as err:
                print(err, 'Try again')
            else:
                rotors.append(tmp.pop(choice - 1))
                print('Choose rotor offset (A - Z):')
                try:
                    choice = input('Your choice: ')
                    if not 'A' <= choice <= 'Z':
                        raise Exception('Invalid choice! ')
                except Exception as err:
                    print(err, 'Try again')
                else:
                    offset += choice
        print('Choose reflector: ')
        for i in range(len(list(reflectorCollection.keys()))):
            print(str(i + 1) + ': ' + list(reflectorCollection.keys())[i])
        try:
            choice = int(input('Your choice: '))
            if not 1 <= choice <= len(list(reflectorCollection.keys())):
                raise Exception('Invalid choice! ')
        except Exception as err:
            print(err, 'Try again')
        else:
            reflector = list(reflectorCollection.keys())[choice - 1]
        print('Chosen settings: ' + str({'rotors': rotors, 'reflector': reflector, 'offset': offset}))
        text = input('Enter message to encrypt: ')
        print(Enigma(text, rotors, reflector, offset))

    def SimBombe():
        text = input('Enter encrypted text: ')
        guess = input('Enter phrase to check: ')
        settings = Bombe(text, guess)

    flag = True
    while flag:
        print(menu)
        try:
            choice = int(input('Your choice: '))
            if not 1 <= choice <= 3:
                raise Exception('Invalid choice! ')
        except Exception as err:
            print(err, 'Try again')
        else:
            if choice == 1:
                SimEnigma()
            elif choice == 2:
                SimBombe()
            else:
                flag = False


Main()
