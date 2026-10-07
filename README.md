# [Flashcards](https://flashcards.korz.org/)

A flashcards web app that runs entirely in the browser.

## Stack

- [Next.js 16](https://nextjs.org/), statically exported and hosted on GitHub
  Pages
- [TypeScript 6](https://www.typescriptlang.org/)
- [Tailwind CSS 4](https://tailwindcss.com/)

## Development

Prerequisites: [nvm](https://github.com/nvm-sh/nvm). The project requires the
current Node.js LTS release and npm 11.11 or later, which the LTS release
bundles.

```sh
nvm install
npm install
npm run dev
```

The dev server is reachable at http://localhost:3000. To reach it through other
hostnames, set `NEXT_ALLOWED_DEV_ORIGINS` to a comma-separated list of them:

```sh
NEXT_ALLOWED_DEV_ORIGINS=myhost.local,192.168.1.10 npm run dev
```

Run `npm run verify` to run all checks.

## License

[MIT](LICENSE)
