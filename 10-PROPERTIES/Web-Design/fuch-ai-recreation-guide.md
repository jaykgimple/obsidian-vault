# fuch.ai — How to Recreate It

**URL**: https://www.fuch.ai  
**Author**: Sayandeep Bose (Sr. CX/UX Designer, Digital Dubai)  
**Tagline**: "A portfolio you meet, not read"

## What It Is

Not a normal portfolio. A living, explorable 3D world where you meet Fuch, a robot who:
- Watches your cursor and reacts
- Gets bored if you ignore him
- Falls asleep if you leave
- Remembers you when you come back

Behind the robot: an AI that answers for its maker, and IDEA52 — an explorable world hiding 52 weekly ideas. Ten years of CX design, alive.

## Awards

- Awwwards Honorable Mention (Jul 19, 2026)
- CSS Design Awards winner
- CSS Winner Site of the Day
- Featured on Dribbble

## Technology Stack

| Layer | Technology | Purpose |
|---|---|---|
| **Framework** | React | UI foundation |
| **3D Engine** | Three.js | 3D rendering |
| **Renderer** | React Three Fiber (R3F) | React renderer for Three.js |
| **Graphics API** | WebGL + WebGPU | GPU-accelerated rendering |
| **Shaders** | GLSL / WGSL | Custom visual effects |
| **Animation** | Framer Motion / React Spring | UI animations |
| **AI/LLM** | Custom (likely Claude/GPT) | Chat interface that "answers for its maker" |
| **State** | Zustand / Jotai | Global state (mood system) |
| **Styling** | Tailwind CSS | Utility-first styling |
| **Build** | Vite / Next.js | Build tool |

## Core Features to Recreate

### 1. The Robot (Fuch) — Cursor-Reactive 3D Character

**What it does**: Follows your cursor. Has moods. Reacts to interaction (or lack thereof).

**How to build it**:
- Load a 3D model (GLTF/GLB) of the robot in React Three Fiber
- Use `useFrame` to lerp the robot's head/eyes toward cursor position
- Track cursor position globally (mouse/touch events)
- Add a mood state machine (happy, bored, sleepy, curious)
- Timeout system: no interaction → bored → asleep
- Re-interaction → wakes up, remembers you (could use localStorage for "memory")

```jsx
// Pseudocode for cursor following
function Robot() {
  const meshRef = useRef()
  const mouse = useThree((state) => state.mouse)
  
  useFrame(() => {
    // Smoothly rotate head toward cursor
    meshRef.current.rotation.y = lerp(meshRef.current.rotation.y, mouse.x * 0.5, 0.1)
    meshRef.current.rotation.x = lerp(meshRef.current.rotation.x, mouse.y * 0.3, 0.1)
  })
  
  return <mesh ref={meshRef}>{/* robot model */}</mesh>
}
```

### 2. The Explorable World (IDEA52)

**What it does**: A 3D world with 52 hidden "idea" nodes you can discover.

**How to build it**:
- Create a 3D environment (terrain, floating islands, abstract space)
- Place 52 interactive nodes/objects in the world
- Orbit controls or first-person navigation
- Raycasting to detect clicks on ideas
- Each idea opens a modal/panel with content

```jsx
// Pseudocode for explorable world
function World() {
  return (
    <>
      <Environment preset="night" />
      <OrbitControls />
      {ideas.map((idea, i) => (
        <IdeaNode key={i} position={idea.position} content={idea.content} />
      ))}
    </>
  )
}
```

### 3. AI Chat Interface

**What it does**: An AI that answers questions about Sayandeep/his work.

**How to build it**:
- Chat UI overlay (bottom-right corner, slides up)
- Connect to Claude API or GPT-4
- System prompt: persona of Sayandeep, his background, projects, style
- Streaming responses
- Optional: voice input/output

### 4. Mood System

**What it does**: Robot has visible emotional states based on user behavior.

**How to build it**:
- Global state (Zustand) tracking: lastInteractionTime, currentMood
- Mood states: idle → curious → happy → bored → sleepy → asleep
- Visual changes per mood: posture, color, animation speed, facial expression
- Idle timer: 30s no interaction → bored, 2min → asleep
- Re-interaction: wakes up with a "welcome back" animation

### 5. Memory System

**What it does**: Remembers returning visitors.

**How to build it**:
- localStorage to store visit count, last visit date, interactions
- On load: if returning, robot says "Welcome back!"
- Could track which ideas you've discovered
- Show "You've found X of 52 ideas"

## Implementation Architecture

```
fuch.ai/
├── public/
│   ├── models/
│   │   └── fuch-robot.glb          # 3D robot model
│   ├── textures/
│   │   └── environment/             # HDRIs, textures
│   └── og-image.jpg
├── src/
│   ├── components/
│   │   ├── Robot/
│   │   │   ├── Robot.tsx            # Main robot component
│   │   │   ├── RobotModel.tsx       # GLTF loader
│   │   │   ├── RobotEyes.tsx        # Eye tracking
│   │   │   └── RobotMoods.tsx       # Mood-based animations
│   │   ├── World/
│   │   │   ├── World.tsx            # 3D environment
│   │   │   ├── IdeaNode.tsx         # Interactive idea markers
│   │   │   └── Environment.tsx      # Lighting, skybox, fog
│   │   ├── UI/
│   │   │   ├── Chat.tsx             # AI chat interface
│   │   │   ├── Navigation.tsx       # Wayfinding UI
│   │   │   └── Loader.tsx           # Loading screen
│   │   └── Effects/
│   │       ├── Particles.tsx        # Particle systems
│   │       └── PostProcessing.tsx   # Bloom, vignette, etc.
│   ├── hooks/
│   │   ├── useMood.ts               # Mood state machine
│   │   ├── useMemory.ts             # localStorage persistence
│   │   └── useCursor.ts             # Global cursor tracking
│   ├── store/
│   │   └── useStore.ts              # Zustand global state
│   ├── data/
│   │   └── ideas.ts                 # 52 ideas content
│   └── App.tsx
```

## Key Libraries

```bash
npm install three @react-three/fiber @react-three/drei
npm install zustand
npm install framer-motion
npm install @anthropic-ai/sdk  # For AI chat
npm install leva  # Debug GUI
npm install @react-three/postprocessing  # Bloom, etc.
```

## Step-by-Step Build Plan

### Phase 1: Foundation
1. Set up React + Vite + TypeScript
2. Install React Three Fiber + Drei
3. Create basic 3D scene with orbit controls
4. Add environment lighting

### Phase 2: The Robot
1. Model or source a robot 3D model (GLTF)
2. Load model with `@react-three/drei`'s `useGLTF`
3. Implement cursor-following behavior
4. Add idle animation (subtle breathing, looking around)
5. Implement mood state machine

### Phase 3: Interaction & Moods
1. Track global cursor position
2. Track last interaction time
3. Implement mood transitions (curious → bored → asleep)
4. Add visual feedback per mood (color, speed, posture)
5. Implement memory (localStorage)

### Phase 4: The World
1. Build explorable 3D environment
2. Add 52 idea nodes (could be orbs, crystals, floating objects)
3. Implement raycasting for click detection
4. Create idea detail modal/panel
5. Add navigation hints/minimap

### Phase 5: AI Chat
1. Build chat UI overlay
2. Connect to Claude API
3. Write system prompt (persona, background, projects)
4. Implement streaming responses
5. Add to robot's "memory" (context from past chats)

### Phase 6: Polish
1. Post-processing (bloom, depth of field, vignette)
2. Sound design (ambient, interaction sounds)
3. Loading screen
4. Mobile responsiveness
5. Performance optimization (LOD, instancing)

## For Bookbrary Specifically

### How This Pattern Could Apply

1. **Book Characters as Guides** — Instead of a robot, a book character guides you through the library
2. **3D Bookshelf World** — Explorable 3D library with books on shelves you can browse
3. **Reading Mood System** — The guide reacts to your reading habits (finished a book? excited. Haven't visited in a while? sad.)
4. **Discovery System** — Hidden "idea gems" scattered through the library that reveal book recommendations, author facts, lore
5. **AI Librarian** — An AI that answers questions about books, characters, recommends reads

### Tech Stack for Bookbrary

Same as fuch.ai:
- React Three Fiber + Three.js
- WebGPU for performance
- Zustand for state
- Claude API for AI librarian
- Tailwind for UI

## Sources

- https://www.fuch.ai/ — The site itself
- https://dribbble.com/shots/27527538-fuch-ai-a-portfolio-you-meet-not-read — Dribbble breakdown
- https://www.awwwards.com/sites/fuch-ai — Awwwards writeup
- https://www.csswinner.com/details/fuchai/19323 — CSS Winner
- https://www.cssdesignawards.com/sites/fuch-ai/49738/ — CSS Design Awards
- https://gist.github.com/sbfuchai — Author's GitHub gists
- https://ae.linkedin.com/in/sayandeep-b — LinkedIn
