# CareerLens Frontend

This template provides a minimal setup to get React working in Vite with HMR and some ESLint rules.

Currently, two official plugins are available:

- [@vitejs/plugin-react](https://github.com/vitejs/vite-plugin-react/blob/main/packages/plugin-react) uses [Oxc](https://oxc.rs)
- [@vitejs/plugin-react-swc](https://github.com/vitejs/vite-plugin-react/blob/main/packages/plugin-react-swc) uses [SWC](https://swc.rs/)

## React Compiler

The React Compiler is not enabled on this template because of its impact on dev & build performances. To add it, see [this documentation](https://react.dev/learn/react-compiler/installation).

## Expanding the ESLint configuration

If you are developing a production application, we recommend using TypeScript with type-aware lint rules enabled. Check out the [TS template](https://github.com/vitejs/vite/tree/main/packages/create-vite/template-react-ts) for information on how to integrate TypeScript and [`typescript-eslint`](https://typescript-eslint.io) in your project.

## CareerLens Development

This frontend provides state-based navigation for the CareerLens features and calls the FastAPI backend at `http://127.0.0.1:8000`. React Router is not used.

From this directory:

```powershell
npm install
npm run dev
```

The Vite development server runs on `http://localhost:5174`.

Validate the frontend with:

```powershell
npm run lint
npm run build
```

See the root [README](../README.md), [DEMO_FLOW](../DEMO_FLOW.md), and [CAREERLENS_INTERVIEW_NOTES](../CAREERLENS_INTERVIEW_NOTES.md) for the complete project documentation.
