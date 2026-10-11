# Evaluation: injected contradictions

**date:** 2026-10-05 · **model:** qwen3:4b-instruct · **extraction:** v4 · **checker:** v2 · **chapters:** 24 · **test corpus check:** 185 LLM calls, 2691s · **original book check:** 265 LLM calls, 3686s

## Summary

| Measure | Value |
|---|---|
| Injected contradictions | 20 |
| Detected (recall) | 5 (25%) |
| Detected in the injected chapter itself | 5 |
| Flags raised on the test corpus | 112 |
| Flags that point at an injected contradiction (precision) | 8 (7%) |
| False alarms on harmless control edits | 0 |
| Confidence tier matches the expected tier | 40% |
| Flags on the original, unedited book (all false alarms) | 111 |

## Recall by category

| Category | Injected | Detected | Recall |
|---|---|---|---|
| characterisation | 7 | 3 | 43% |
| factual_detail | 3 | 0 | 0% |
| timeline | 4 | 1 | 25% |
| world_building | 6 | 1 | 17% |

## Precision by confidence tier

| Tier | Flags | Pointing at an injection | Precision |
|---|---|---|---|
| high | 16 | 2 | 12% |
| medium | 24 | 4 | 17% |
| low | 72 | 2 | 3% |

## Every injected contradiction

| Id | Ch | Category | Injected text | Detected | Expected tier | Flagged tier | Checker's reason |
|---|---|---|---|---|---|---|---|
| I01 | 8 | characterisation | It was true; Toto, the little white dog, had fallen down beside his little mistress. | **no** | high | - |  |
| I02 | 10 | characterisation | and even on little Toto, whose black coat now looked quite green through the glasses; and… | **no** | low | - |  |
| I03 | 11 | factual_detail | “Send me back to Kansas, where my Aunt Em and Uncle Henry, the village blacksmith, are,” … | **no** | high | - |  |
| I04 | 24 | characterisation | Aunt Em, her bright blue eyes sparkling, had just come out of the house to water the cabb… | yes | high | high | Earlier, in chapter 1, Aunt Em's eyes are described as 'sober gray' due to the effects of hardship. In chapter 24, her eyes are described a… |
| I05 | 9 | characterisation | because his head was stuffed with sawdust | yes | high | high | Earlier, it was established in chapter 6 that the Scarecrow's head is stuffed with straw. The new statement in chapter 9 claims his head is… |
| I06 | 11 | factual_detail | when I mentioned your golden shoes he was very much interested. | **no** | high | - |  |
| I07 | 14 | world_building | that is how it happens that we are forever, without any limit, the slaves of the owner of… | **no** | high | - |  |
| I08 | 18 | world_building | She is the most wicked of all the Witches, and rules cruelly over the Quadlings. | **no** | high | - |  |
| I09 | 11 | world_building | Dorothy and her friends were at first dazzled by the brilliancy of the wonderful City, th… | **no** | high | - |  |
| I10 | 13 | world_building | the Wicked Witch had been burned up in her own kitchen fire | yes | high | medium | The earlier facts establish that the Lion is initially unwilling to harm Dorothy and expresses cowardice, yet agrees to go with her. The ne… |
| I11 | 10 | world_building | while in the country of the Munchkins red was the favorite color. | **no** | high | - |  |
| I12 | 8 | timeline | “For many long years I was stuck on a pole in a cornfield | **no** | high | - |  |
| I13 | 6 | timeline | I stood rusting in the forest for only a single day, but I am not afraid so long as I hav… | yes | high | medium | The earlier facts establish that the Tin Woodman has a jointed body made entirely of tin, with a shiny, rigid appearance. The new statement… |
| I14 | 7 | characterisation | “Ah,” said the Tin Woodman sadly, “I wish I had brains to think with, for I never cared f… | yes | high | low | The earlier facts establish that the Tin Woodman is polite, grateful, and not afraid—showing a calm, resilient, and emotionally composed pe… |
| I15 | 10 | characterisation | “And I want him to give me a heart, for I have plenty of courage,” said the Cowardly Lion. | **no** | high | - |  |
| I16 | 4 | factual_detail | So she told him all about Kansas, and how green and bright everything was there | **no** | medium | - |  |
| I17 | 2 | characterisation | The men, Dorothy thought, were about as old as Uncle Henry, though unlike clean-shaven Un… | **no** | high | - |  |
| I18 | 12 | world_building | But, in truth, she did not dare to strike Dorothy, although the faded mark upon her foreh… | **no** | low | - |  |
| I19 | 3 | timeline | “Because you wear silver shoes and have killed the Wicked Witch, who had ruled us for onl… | **no** | high | - |  |
| I20 | 17 | timeline | “You see, when I came to this country only last spring, it was in a balloon. | **no** | high | - |  |

## False alarms on the test corpus (104)

| Ch | Entity | New statement | Earlier fact | Tier | Checker's reason |
|---|---|---|---|---|---|
| 2 | Dorothy | relationship_to_dorothy: only friend | ch1 relationship_to_aunt_em: with Aunt Em | low | Earlier, Dorothy is established as living with Uncle Henry and Aunt Em, indicating a familial relationship with them. The new statement des… |
| 3 | Dorothy | appearance: gingham, with checks of white and blue | ch2 eye_colour: growing bigger | low | The earlier fact describes Dorothy's eyes growing bigger in response to the wonders around her, focusing on her emotional and physical reac… |
| 3 | Dorothy | dress_colour: white and blue checks | ch2 eye_colour: growing bigger | low | The earlier fact establishes that Dorothy's eyes are growing bigger in response to the wonders around her, describing a physical and emotio… |
| 3 | Dorothy | dress_condition: somewhat faded | ch2 eye_colour: growing bigger | low | The earlier fact establishes that Dorothy's eyes are growing bigger in response to the wonders around her, describing a physical and emotio… |
| 3 | Dorothy | relationship_to_toto: gave food to | ch2 relationship_to_dorothy: only friend | low | Earlier, in chapter 2, Dorothy is described as having only one friend, the little old woman, indicating a close, personal bond with that fi… |
| 3 | Toto | size: small | ch1 appearance: a little black dog | low | The earlier facts establish that Toto is a 'little black dog' with 'small black eyes' and 'long silky hair,' describing him as small in siz… |
| 3 | Dorothy | home: a Munchkin's home | ch1 living_location: the great Kansas prairies | medium | Earlier, Dorothy is established as living in the great Kansas prairies with Uncle Henry and Aunt Em. The new statement places her in a Munc… |
| 3 | Dorothy | origin: by the chance of a cyclone | ch1 living_location: the great Kansas prairies | low | The earlier fact establishes that Dorothy lives in the Kansas prairies with her farmer relatives, indicating her origin is rooted in that r… |
| 3 | Toto | appearance: a fine curiosity | ch1 appearance: a little black dog | low | The earlier facts establish that Toto is a little black dog with small black eyes. The new statement describes Toto as a 'fine curiosity' t… |
| 3 | Toto | relationship_to_dorothy: new friend of Dorothy | ch1 relationship_to_dorothy: played with Dorothy | high | The earlier fact establishes that Toto is a pet that Dorothy plays with and loves dearly, indicating a close, established relationship. The… |
| 4 | the Scarecrow | mouth: only painted | ch3 eye_colour: painted eyes, nose, and mouth | low | The earlier fact states that the Scarecrow's eyes, nose, and mouth are all painted. The new statement specifies that only the mouth is pain… |
| 4 | the Scarecrow | age: day before yesterday | ch3 age: old | high | The earlier fact establishes that the Scarecrow is old, described as wearing a worn, faded blue suit and an old hat, implying a long-standi… |
| 4 | the Scarecrow | appearance: like a man | ch3 clothing: blue suit of clothes, worn and faded | low | The earlier facts establish that the Scarecrow is made of straw with painted eyes, nose, and mouth, and wears a faded blue suit. The new st… |
| 4 | the Scarecrow | relationship_to_farmer: made by the farmer | ch3 relationship_to_dorothy: helped by Dorothy | low | The earlier fact establishes that the Scarecrow is helped by Dorothy, indicating a relationship between the Scarecrow and Dorothy. The new … |
| 4 | the Scarecrow | relationship_to_munchkin: with another Munchkin | ch3 relationship_to_dorothy: helped by Dorothy | low | The earlier fact establishes that the Scarecrow is helped by Dorothy, indicating a supportive relationship between the Scarecrow and Doroth… |
| 4 | the Scarecrow | size: small | ch3 clothing: blue suit of clothes, worn and faded | low | The earlier facts establish that the Scarecrow has painted eyes, a straw head, and is dressed in a worn, faded blue suit. The new statement… |
| 4 | the Scarecrow | personality: curious and quiet | ch3 personality: does not want to be called a fool | low | The earlier fact establishes that the Scarecrow is aware of his own foolishness and resists being called a fool, showing a sense of self-aw… |
| 4 | the Scarecrow | appearance: hopped down at my feet | ch3 clothing: blue suit of clothes, worn and faded | medium | The earlier facts establish that the Scarecrow has painted eyes, a straw head, and a blue, worn, faded suit. The new statement describes th… |
| 4 | the Scarecrow | personality: uncomfortable feeling to know one is a fool | ch3 personality: does not want to be called a fool | low | The earlier fact establishes that the Scarecrow does not want to be called a fool, expressing a strong desire to avoid being labeled as suc… |
| 4 | the Scarecrow | relationship_to_dorothy: seems anxious to have them | ch3 relationship_to_dorothy: helped by Dorothy | medium | The earlier fact establishes that the Scarecrow helped Dorothy, indicating a cooperative and supportive relationship. The new statement sug… |
| 4 | Dorothy | relationship_to_toto: with Toto beside her | ch3 relationship_to_toto: gave food to | low | The earlier fact establishes that Dorothy gives food to Toto, indicating a relationship of care and companionship. The new statement shows … |
| 4 | Dorothy | occupation: pulled me off the stake | ch3 occupation: a housewife | medium | The earlier fact establishes Dorothy as a housewife, engaged in domestic activities like fetching water. The new statement attributes an ac… |
| 5 | Toto | appearance: chasing birds around him and squirrels | ch3 size: small | low | The earlier facts establish that Toto is a small, black dog with black eyes, described as a curious and lively pet. The new statement in ch… |
| 5 | the Scarecrow | appearance: still standing patiently in his corner | ch3 clothing: blue suit of clothes, worn and faded | low | The new statement describes the Scarecrow as still standing patiently in his corner, which aligns with his earlier appearance as a man-like… |
| 5 | Dorothy | occupation: washes face and drinks water | ch3 occupation: a housewife | low | The earlier fact establishes Dorothy as a housewife in chapter 3, engaged in domestic tasks like filling a pail with water and giving it to… |
| 5 | the Scarecrow | personality: inconvenient to be made of flesh | ch4 personality: curious and quiet | low | The new statement in chapter 5 reflects a shift in the Scarecrow's perspective from being uncomfortable with being called a fool (earlier f… |
| 5 | the Scarecrow | goal: wants Oz to give him brains | ch4 goal: try hard to get some brains | low | The earlier facts establish that the Scarecrow's goal is to acquire brains, both through personal effort (chapter 4) and by following a pat… |
| 5 | the little old woman | relationship_to_name: went to the Wicked Witch of the East | ch2 name: Witch of the North | high | The earlier fact establishes that the little old woman is the Witch of the North and expresses gratitude to Dorothy for killing the Wicked … |
| 5 | the little old woman | relationship_to_name: promised two sheep and a cow | ch2 relationship_to_dorothy: grateful to Dorothy | high | The earlier fact establishes that the little old woman is grateful to Dorothy for defeating the Wicked Witch of the East and freeing her pe… |
| 6 | the Tin Woodman | occupation: has never been to the Emerald City | ch5 occupation: wood-chopper | low | The earlier facts establish that the Tin Woodman has a long-standing occupation as a wood-chopper and has been groaning for over a year, in… |
| 6 | Dorothy | wants_to_return_to_kansas: to send Toto and herself back to Kansas | ch5 goal: want Oz to send her back to Kansas | low | The earlier fact establishes that Dorothy's goal is for Oz to send her back to Kansas, and she mentions the Scarecrow's desire for brains. … |
| 6 | Dorothy | wants_to_be_given_courage: to send Toto and herself back to Kansas | ch5 goal: want Oz to send her back to Kansas | low | The earlier fact establishes that Dorothy's goal is for Oz to send her back to Kansas, and she expresses a desire for the Scarecrow to be g… |
| 6 | the Tin Woodman | is_careful_not_to_hurt_living_creatures: careful not to hurt living creatures | ch5 origin: from Munchkin maiden | low | The earlier facts establish that the Tin Woodman has a cottage in the woods, originates from a Munchkin maiden, and is concerned about rust… |
| 7 | Dorothy | location: under a large tree in the forest | ch1 living_location: the great Kansas prairies | low | Earlier, Dorothy was established as living in the great Kansas prairies with her relatives, and later in chapter 3, her home is described a… |
| 7 | Dorothy | personality: prefer cooked food | ch3 personality: resilient | low | The earlier fact establishes Dorothy as resilient in the face of adversity, showing emotional strength and adaptability. The new statement … |
| 7 | Dorothy | location: bathed her face in a little rippling brook | ch1 living_location: the great Kansas prairies | low | Earlier fact 1 establishes that Dorothy lives in the great Kansas prairies with Uncle Henry and Aunt Em, in a rural, open landscape. The ne… |
| 7 | the Tin Woodman | occupation: builds rafts | ch5 occupation: wood-chopper | low | The earlier facts establish that the Tin Woodman is a wood-chopper by occupation and has been groaning for over a year, with no prior conne… |
| 8 | Dorothy | appearance: sat down in the middle of the raft | ch3 appearance: gingham, with checks of white and blue | low | The earlier facts describe Dorothy's dress (gingham with white and blue checks), her eye color (growing bigger), and the condition of her d… |
| 8 | Dorothy | goal: get back to the road | ch6 wants_to_return_to_kansas: to send Toto and herself back to Kansas | medium | Earlier facts establish that Dorothy's goal is to return to Kansas, specifically to send herself and Toto back to Kansas. The new statement… |
| 8 | the Lion | goal: walk along the riverbank | ch6 wants_courage: to ask Oz for courage | low | The earlier fact establishes that the Lion desires courage, as he explicitly asks Oz for it. The new statement describes the Lion suggestin… |
| 8 | the Scarecrow | relationship_to_dorothy: lost by Dorothy | ch4 relationship_to_dorothy: seems anxious to have them | medium | Earlier, the Scarecrow is described as being helped by Dorothy and showing anxiety about having her presence, indicating a positive, active… |
| 8 | the Scarecrow | location: in the river | ch4 home: on a tall stick in the cornfield | high | The earlier facts establish that the Scarecrow is located in the cornfield, specifically on a tall stick within that field. The new stateme… |
| 8 | the Scarecrow | ability: not made of flesh | ch4 ability: see as well as by day | low | The earlier facts establish that the Scarecrow has the ability to hear and see well, which are physical and sensory capabilities. The new s… |
| 9 | the Scarecrow | location: river carried us away | ch4 home: on a tall stick in the cornfield | low | Earlier facts establish that the Scarecrow is located in the cornfield, specifically on a tall stick, and is associated with the cornfield … |
| 9 | the Scarecrow | occupation: told about everything | ch4 occupation: a scarecrow | low | The earlier fact establishes that the Scarecrow is described as looking like a man, implying a human-like appearance, and is given a role a… |
| 9 | the Scarecrow | ability: brought fruit from a tree | ch8 ability: not made of flesh | low | The earlier facts establish that the Scarecrow has specific sensory and physical abilities—such as hearing and seeing well, and being made … |
| 10 | the Scarecrow | want: some brains | ch4 goal: try hard to get some brains | low | The earlier fact establishes that the Scarecrow's goal is to 'try hard to get some brains,' showing an active effort to acquire intelligenc… |
| 10 | Toto | want: wagged his tail | ch3 behavior: wagged tail | low | The earlier fact establishes that Toto wags his tail as a behavior, specifically when looking up and showing recognition. The new statement… |
| 12 | the Wicked Witch of the West | home: her castle | ch2 home: West | low | The earlier facts establish that the Wicked Witch of the West rules the land of the Winkies in the West, and her domain is tied to that reg… |
| 12 | the Wicked Witch of the West | home: door of her castle | ch2 home: West | low | The earlier facts establish that the Wicked Witch of the West rules the land of the Winkies in the West, and her home is located there. The… |
| 12 | the Lion | location: in a small yard with a high iron fence | ch11 location: the land of the Winkies | high | The earlier fact establishes that the Lion is going to the land of the Winkies to confront the Wicked Witch. The new statement places the L… |
| 12 | the Lion | relationship_to_dorothy: does not like Dorothy | ch11 relationship: will go with Dorothy | high | The earlier fact establishes that the Lion is willing to go with Dorothy and expresses a reluctance to kill the Witch, indicating a friendl… |
| 12 | the Lion | appearance: soft, shaggy mane | ch6 appearance: as big as a small horse | low | The earlier facts establish the Lion's size—comparable to a small horse and heavier than mice—emphasizing its large physical form. The new … |
| 12 | Toto | relationship_to_dorothy: loves Dorothy | ch7 relationship_to_dorothy: held by Dorothy | medium | The earlier facts establish that Toto is a companion to Dorothy—played with her, considered a new friend, and physically held by her. The n… |
| 13 | the Winkies | relationship_to_dorothy: set free by Dorothy | ch12 relationship_to_wicked_witch: are slaves of the Wicked Witch | medium | The earlier fact establishes that the Winkies are slaves of the Wicked Witch and fear her, while the new statement implies that Dorothy set… |
| 14 | Dorothy | ability: three times the right to lay wishes upon us | ch12 power: cannot use shoe power | low | The earlier facts establish that Dorothy is protected by the Power of Good and cannot use the shoes' power due to a magical constraint. The… |
| 14 | Dorothy | personality: friendly, appreciative | ch3 personality: resilient | low | The earlier facts establish Dorothy as resilient (chapter 3) and with a preference for cooked food (chapter 7), both of which describe aspe… |
| 14 | the Lion | relationship_to_dorothy: acknowledges Dorothy's action | ch11 relationship: will go with Dorothy | medium | The new statement in chapter 14 acknowledges Dorothy's action—bringing the cap—which implies a positive recognition of her role, aligning w… |
| 15 | Dorothy | age: only once | ch4 age: all tired out | low | Earlier, in chapter 4, Dorothy is described as 'all tired out,' suggesting she is physically and emotionally exhausted, which implies a sta… |
| 15 | Dorothy | ability: melted the Wicked Witch | ch12 power: cannot use shoe power | medium | Earlier, it was established that Dorothy cannot use the power of the shoes (fact 3), and that she is protected by the Power of Good (fact 2… |
| 15 | the soldier | occupation: on guard before the door | ch11 occupation: took her message to the Wizard | low | The earlier fact establishes that the soldier took Dorothy's message to the Wizard and was involved in a specific role at the palace. The n… |
| 15 | Oz | location: Throne Room | ch11 location: before the throne was a Ball of Fire | low | The earlier fact establishes that before the throne in the land of the Winkies there was a Ball of Fire, and that the Lion plans to go to t… |
| 15 | Oz | identity: Great and Terrible | ch2 identity: Great Wizard | medium | The earlier fact establishes Oz as the 'Great Wizard,' a title emphasizing his wisdom and authority. The new statement introduces 'Great an… |
| 15 | Oz | ability: throw voice wherever | ch11 ability: alone have power to grant my request | low | The earlier facts establish that Oz has the ability to grant brains and to independently fulfill requests due to being the greatest wizard.… |
| 15 | Oz | location: rear of the Throne Room | ch11 location: before the throne was a Ball of Fire | low | The earlier fact establishes that before the throne was a Ball of Fire, and that the Lion plans to go to the land of the Winkies to destroy… |
| 15 | Toto | relationship_to_oz: fool everyone | ch12 relationship_to_dorothy: loves Dorothy | low | The earlier facts establish Toto's relationship with Dorothy—his companionship, friendship, and emotional bond with her. The new statement … |
| 15 | Oz | occupation: balloonist | ch2 occupation: Great Wizard | high | Earlier, Oz is established as the Great Wizard in chapter 2. In chapter 15, Oz is described as a balloonist, which contradicts his earlier … |
| 15 | Oz | occupation: very old man | ch2 occupation: Great Wizard | low | The earlier fact establishes that Oz is the Great Wizard, a title of authority and power. The new statement describes Oz as a very old man,… |
| 15 | Oz | personality: very good man, very bad Wizard | ch11 personality: does not grant favors without return | medium | The earlier fact establishes that Oz is principled and operates on the principle of reciprocity—favors are only granted if there is return.… |
| 15 | Oz | relationship_to_dorothy: promised anything if she would do away with the o… | ch11 relationship_to: would admit you to his presence | medium | Earlier, in chapter 11, Oz is portrayed as a figure who is initially angry but eventually admits Dorothy to his presence after she reveals … |
| 15 | Oz | ability: no magical powers | ch11 ability: can give brains to others | high | The earlier facts establish that Oz has magical powers—such as granting brains and independently fulfilling requests—while the new statemen… |
| 15 | Oz | personality: believes experience brings knowledge | ch11 personality: does not grant favors without return | medium | The new statement introduces a shift in Oz's personality by emphasizing learning through experience, which contrasts with the earlier estab… |
| 15 | Oz | personality: continues the role of a Wizard | ch11 personality: does not grant favors without return | low | The earlier fact establishes that Oz is principled and conditional in granting favors, emphasizing a strict 'no favors without return' poli… |
| 15 | Oz | personality: cannot keep promises | ch11 personality: does not grant favors without return | high | The earlier fact establishes that Oz grants favors only with return, and explicitly promises something under condition. The new statement c… |
| 15 | Oz | personality: believes courage comes from confidence | ch11 personality: does not grant favors without return | low | The earlier fact establishes that Oz does not grant favors without return, emphasizing a principle of reciprocity. The new statement introd… |
| 15 | Oz | personality: thinks hearts make people unhappy | ch11 personality: does not grant favors without return | medium | The earlier fact establishes that Oz is principled and demands return for any favor, showing a consistent, transactional attitude toward re… |
| 15 | the spectacles | appearance: worn by all people | ch10 appearance: green glasses | high | Earlier, in chapter 10, the spectacles were described as green glasses worn only by a specific individual (a woman) with two golden bands a… |
| 15 | the spectacles | appearance: everything looks green | ch10 appearance: green glasses | low | Earlier, the spectacles were described as green glasses with two golden bands and locked together by a key. The new statement introduces gr… |
| 15 | the Emerald City | nature: has all good things needed to make one happy | ch11 building_material: green marble | low | The earlier facts establish that the Emerald City is made of green marble and has green glass windows, with a green-tinted sky and green su… |
| 15 | Oz | relationship_to_dorothy: helps Dorothy return to Kansas | ch11 relationship_to: would admit you to his presence | medium | Earlier, in chapter 11, Oz is portrayed as a figure who is initially angry but eventually admits Dorothy to his presence and shows interest… |
| 15 | Oz | occupation: finds a way across the desert | ch2 occupation: Great Wizard | low | The earlier fact establishes that Oz is the Great Wizard, a role of authority and magical power. The new statement describes Oz as someone … |
| 15 | Oz | personality: makes a small, conditional offer | ch11 personality: does not grant favors without return | medium | The earlier fact establishes that Oz is strict about returning favors, refusing to grant anything without a condition. The new statement sh… |
| 15 | Oz | personality: is called a humbug | ch11 personality: does not grant favors without return | low | Earlier, Oz is described as someone who does not grant favors without return, showing a principled and conditional personality. The new sta… |
| 15 | Oz | relationship_to_dorothy: treats Dorothy as a guest | ch11 relationship_to: would admit you to his presence | low | Earlier, in chapter 11, Oz is described as someone who initially reacts with anger and skepticism toward Dorothy, but eventually admits her… |
| 15 | Oz | relationship_to_dorothy: is a humbug | ch11 relationship_to: would admit you to his presence | high | Earlier, Oz is portrayed as a figure who is initially angry but eventually admits Dorothy to his presence and shows interest in her appeara… |
| 16 | the Scarecrow | occupation: to get my brains | ch11 occupation: a Scarecrow | high | The earlier facts establish that the Scarecrow is a literal, straw-filled scarecrow with no consciousness or intelligence—his occupation is… |
| 17 | the soldier | occupation: fastened many ropes | ch15 occupation: on guard before the door | medium | The earlier facts establish that the soldier has a consistent occupation involving guarding and delivering messages, notably with green whi… |
| 17 | the soldier | size: more than twenty feet long | ch15 appearance: green whiskers | low | The earlier fact establishes that the soldier has green whiskers and is present in a scene involving a 'beautiful green girl' and a guard p… |
| 18 | the Scarecrow | occupation: ruler of the Emerald City | ch4 occupation: a scarecrow | medium | Earlier facts establish that the Scarecrow is a non-intelligent, straw-filled figure with a simple, humble identity—described as a scarecro… |
| 18 | the King Crow | knowledge: there has never been a Winged Monkey in Kansas yet | ch14 species: Winged Monkey | high | The earlier fact establishes that the King Crow is a Winged Monkey, specifically identified as 'the King himself' among large monkeys. The … |
| 18 | the road | appearance: straight to the South | ch7 appearance: yellow brick road | low | The earlier fact establishes that the road is a yellow brick road, described as being within a forest and leading toward sunshine. The new … |
| 19 | Dorothy | personality: felt kindly treated | ch14 personality: friendly, appreciative | low | The new statement in chapter 19 describes Dorothy as feeling 'kindly treated' in a city, which aligns with her established personality trai… |
| 20 | Dorothy | personality: thoughtful and considerate | ch19 personality: felt kindly treated | low | The earlier facts establish Dorothy as resilient, having a preference for cooked food, friendly and appreciative, and feeling kindly treate… |
| 20 | Dorothy | personality: kind and tolerant | ch14 personality: friendly, appreciative | low | The new statement in chapter 20 describes Dorothy as kind and tolerant, which aligns with her established personality traits of being resil… |
| 20 | Dorothy | personality: empathetic and sincere | ch19 personality: felt kindly treated | low | The new statement describes Dorothy as empathetic and sincere, which aligns with her established traits of resilience, friendliness, and ap… |
| 20 | the Lion | ability: can carry others | ch7 ability: shook his shaggy mane and looked thoughtful | low | The earlier facts establish that the Lion has physical abilities such as shaking his mane, leaping through the air, swimming, and eventuall… |
| 20 | the Lion | ability: can knock over objects | ch7 ability: shot through the air and landed safely | low | Earlier, the Lion is described as having abilities such as shaking his shaggy mane, leaping through the air, swimming, and eventually givin… |
| 22 | the Winged Monkeys | ability: can carry travelers over hills | ch12 ability: have immense and powerful wings | low | The earlier fact establishes that the Winged Monkeys have immense and powerful wings, which are visually and dramatically described as cove… |
| 22 | the Winged Monkeys | ability: can land travelers near a farmhouse | ch12 ability: have immense and powerful wings | low | The earlier fact establishes that the Winged Monkeys have immense and powerful wings, visible and active in a dramatic scene. The new state… |
| 22 | the Winged Monkeys | ability: can vanish into the air quickly | ch12 ability: have immense and powerful wings | low | The earlier fact establishes that the Winged Monkeys have immense and powerful wings, visible and present in a crowd, with a specific descr… |
| 22 | the Winged Monkeys | location: near a farmhouse | ch14 origin: long before Oz came out of the clouds | low | The earlier facts establish that the Winged Monkeys originated in the great forest and lived there long before Oz emerged from the clouds. … |
| 23 | the Scarecrow | desired_destination: return to the Emerald City | ch8 goal: get to the Emerald City | low | The earlier fact establishes that the Scarecrow's goal is to reach the Emerald City, while the new statement shifts the objective to return… |
| 23 | the silver shoes | ability: carry you to any place in the world in three steps | ch12 power_source: give power to Witch | low | The earlier fact establishes that the Silver Shoes are a power source that replenishes the Witch's energy, specifically giving her more pow… |
| 24 | Aunt Em | appearance: folding the little girl in her arms | ch1 body_shape: thin and gaunt | medium | The earlier facts describe Aunt Em as having sober gray eyes and cheeks, and a thin, gaunt body, all resulting from a past trauma that drai… |
