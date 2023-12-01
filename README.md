## Metode for automatisk generere roder for dør-til-dør aksjoner
Forslag til metode for automatisk generere roder / polygoner som deler inn befolkningen i passe store områder som kan besøkes i løpet av et par timers arbeid

### Befolkningsdata
Analysen tar utgangspunkt i at boenheter fra Matrikkelen representerer husstander som skal besøkes i en dør-til-dør aksjon

1. Ta ut bruksenheter fra Matrikkelen for ønsket område
2. Filtrere ut bruksenheter som har bruksenhetstype 'Bolig'

### Luke ut svært avsidesliggende områder
1. Lag en OD matrise for alle bruksenheter
2. Kalkulere og summere gangavstand til f.eks 10 nærmeste naboer for hver bruksenehet. Denne indeksen kan brukes som vekt når rodene skal skapes for å unngå roder med mange lange avstander.
3. Luk ut boenheter som har mer enn xxx. m/min gangtid til nærmeste nabo

### Interesseområde
For å få et "penere" resultat bør det lages et interesseområde som dekker området hvor det bor folk, men klipper bort vann eller områder langt fra befolkning

1. Lag et buffer rundt alle boenheter fra forrige kapittel, bruk en høy distanse på f.eks. 1000m for å slå sammen nærliggende områder. 
2. Lag en ny buffer av resultatet med en negativ verdi på f.eks. 90% av den forrige bufferdistansen for å få en tettere ytre omkrets rundt boenhetene.

### Lage roder
Analysen trenger å vite hvor mange roder som skal genereres for det valgte området. Basert på erfaringstall fra Sandnes kommune kan følgende formel benyttes:
´´´
antall_boenheter / 60 = antall_roder
´´´
Alternativt kan antall roder vektes basert på punktenes spredning. Områder med spredte bruksenheter får dermed færre bruksenheter pr rode.
1. Kalkulere gjennomsnittsavstand mellom alle punktene i området. Benytte formelen:
´´´
antall_boenheter / (62.5 - min_dist_index * 50)
´´´

#### Lage roder
Rodene lages ved å gjøre en location-allocation analyse hvor boenheter både er 'demand points' og 'facilities'. Det er mulig å sette et tak for antall boenheter som kan allokeres til en rode.

1. Gjøre en Location-Allocation analyse hvor alle boenhetene både er demand points og facilities
2. Hente ut alle 'demand points' fra analysen som nå har en facility-id
3. Lage Thiessen-polygoner av punktene, ta med alle egenskaper
4. Bruk 'Dissolve' til å slå sammen polygoner med lik facility-id

### Etterprossering av data
For et penere resultat bør de sammenslåtte Thiessen-polygonene klippes til interesseområdet. 

1. Klipp Thiessen-polygonene mot interesseområdet
