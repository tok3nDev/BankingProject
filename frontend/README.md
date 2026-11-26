# Banking Project — Frontend

React and TypeScript frontend for the Banking Project application.

## Tech Stack

- React 19
- TypeScript 6
- Vite 8
- Tailwind CSS 4
- React Router 7
- TanStack Query 5
- shadcn/ui with Base UI
- Axios
- Recharts
- Lucide React

## Requirements

- Node.js
- npm
- Running Banking Project backend

## Installation

From the project root:

```bash
cd frontend
npm install
```

## Development

Start the development server:

```bash
npm run dev
```

The application is available at:

http://localhost:5173

## Production Build

Create a production build:

```bash
npm run build
```

Preview the production build locally:

```bash
npm run preview
```

## Code Quality

Run ESLint:

```bash
npm run lint
```

Run TypeScript checks:

```bash
npx tsc --noEmit
```

## Application Routes

| Route | Description | Status |
|---|---|---|
| `/` | Dashboard and application statistics | Implemented |
| `/customers` | Customer list and management | Implemented |
| `/customers/:id` | Customer details and financial profile | Implemented |
| `/applications` | Credit application list and management | Implemented |
| `/applications/:id` | Application details, assessment, and decisions | Implemented |
| `/credit-scoring` | Standalone credit scoring page | Placeholder |
| `/decisions` | Standalone decisions page | Placeholder |
| `/ai-assistant` | AI assistant page | Placeholder |
| `/settings` | Application settings page | Placeholder |

Credit assessment and decision management are currently available within Application Details. The standalone Credit Scoring and Decisions routes are placeholders.

## Architecture

The frontend uses a feature-based structure:

```text
src/
├── app/                  # Application setup, providers, and routing
├── assets/               # Static assets
├── components/
│   ├── layout/           # Application layout
│   ├── shared/           # Shared components
│   └── ui/               # UI primitives
├── features/
│   ├── ai-assistant/
│   ├── applications/
│   ├── credit-scoring/
│   ├── customers/
│   ├── dashboard/
│   └── decisions/
├── lib/                  # API client and shared utilities
└── types/                # TypeScript API types
```

Each feature can contain its own components, hooks, services, and supporting logic.

## Data Management

The API base URL can be configured through `VITE_API_URL`.

If not specified, the frontend uses:

`http://localhost:8000/api/v1`
- Axios is used for HTTP communication with the backend.
- TanStack Query manages server state, caching, and query invalidation.
- Shared API and domain types are defined in `src/types/`.


The backend API uses the `/api/v1` prefix.

## Implemented Features

- Customer creation, listing, and profile editing.
- Credit application creation, listing, and details.
- Credit assessment execution and result display.
- Credit decision creation and decision history.
- Dashboard statistics with automatic refresh after data mutations.

## Scope and Limitations

The frontend implements the core MVP user interface.

The credit scoring workflow uses the backend's rule-based assessment engine. It is not a validated machine learning system and must not be used for real lending decisions.

AI Assistant and Settings pages are currently placeholders.
