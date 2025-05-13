// eslint-disable-next-line no-undef
module.exports = {
  '**/*.{js,jsx,ts,tsx}': (files) => [
    `npx prettier --write ${files.join(' ')}`,
    `npx eslint --fix ${files.join(' ')} --max-warnings=0`
  ],
  '**/*.py': [
    'cd backend && poetry run ruff check --fix',
    'cd backend && poetry run ruff format',
    () => 'pnpm run lintPython'
  ],
  '.github/{workflows,actions}/**': ['actionlint']
};
