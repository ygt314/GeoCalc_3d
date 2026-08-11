# Documentation

## Unknowns

The name of an unknown can be:

- a lowercase English letter (except `x`, `y`, `z`)
- the English name of a Greek letter (except `pi`)

## Points

Point names must be uppercase English letters. Subscripts and superscripts are not supported. ~~(If you ever need more than 26 points... well, good luck.)~~

## Expressions

Our expression parser is built on Python's `eval` ~~(which means you can totally inject arbitrary code and attack the backend)~~, with some custom extensions on top.

### Operations

|   Code    |    Meaning    |
| :-------: | :-----------: |
|    `+`    |   Addition    |
|    `-`    |  Subtraction  |
|    `*`    | Multiplication |
|    `/`    |   Division    |
|   `dot`   |  Dot product  |
|  `cross`  | Cross product |
| `^` or `**` | Exponentiation |

Note: The multiplication symbol `*` is required and cannot be omitted.

### Constants and Functions

|  Code  |   Meaning   |
| :----: | :---------: |
|  `pi`  |    $\pi$    |
| `sqrt` | Square root |
| `sin`  |    Sine     |
| `cos`  |   Cosine    |
| `tan`  |   Tangent   |

Note: Functions must be called with parentheses.

- ❌ Incorrect: `sin pi`
- ✅ Correct: `sin(pi)`

### Accessing Unknowns

Simply type the name you assigned when creating them.

For example: `a`, `alpha`

### Accessing Point Coordinates

Format: `x` / `y` / `z` followed by the point name

For example: `xA` represents $x_A$

### Segment Length

Just type the segment name directly.

For example: `AB` represents the length of segment $AB$

### Angles

1. `ang` + three points that define the angle

For example: `angABC` represents $\angle ABC$

2. `angv` + two vectors (omit `vec`)

For example: `angvABCD` represents $< \overrightarrow{AB}, \overrightarrow{CD} >$

3. `angr` + dihedral angle (omit the hyphen `-`)

For example: `angrABCD` represents $\angle A-BC-D$

4. `angc` + two lines/planes (do NOT omit the underscore `_`)

For example: `angcAB_CD` represents the angle between AB and CD; `angcABC_MN` represents the angle between plane ABC and MN

#### Degrees

Use `deg` to represent degrees ($^{\circ}$)

For example: `30 deg` means $30^{\circ}$

### Vectors

#### Vectors Represented by Directed Segments

Format: `vec` + starting point + ending point

For example: `vecAB` represents $\overrightarrow{AB}$

#### Vectors in Coordinate Form

Format: (x-component, y-component, z-component)

For example: `(114, 514, 666)` represents the vector $(114, 514, 666)$

#### Normal Vectors

Format: `n` + plane name

For example: `nABC` represents $\overrightarrow{n}_{plane ABC}$

### Area of Triangle

Format: `St` + the triangle's three vertices

For example: `StABC` represents the area $S_{\triangle ABC}$

### Volume of Tetrahedron

Format: `v` + the tetrahedron

For example: `vABCD` represents the volume $V_{tetrahedron A-BCD}$

### Distance from Point to Line (Plane)

Format: `d` + point name + `t` + line (plane) name

For example: `dAtBC` represents the distance from point A to line BC, denoted $d_{A \to BC}$; `dAtBCD` represents the distance from point A to plane BCD, denoted $d_{A \to plane BCD}$

**Note!!!** Line-line distance, line-plane distance, and plane-plane distance must all be converted to point-to-XXX distance.

## FAQ

### How to represent circles, parabolas, and other shapes?

Studying these shapes is essentially studying the points on them. You can relate the coordinates of a point with a relation, e.g. $x_A^2 + y_A^2 = 1$ or $y_A = 11 x_A^2 + 45 x_A + 14$. For a circle, you can represent a point on the circle as "a point at distance radius from the center", and a tangent line as "a line at distance radius from the center".
