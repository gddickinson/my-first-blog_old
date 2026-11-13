// Entry point: registers the pages (loaded on first visit) and starts the router.
import { $, isStatic, lazy, start } from './core.js';

lazy({
  home: () => import('./home.js'),
  how: () => import('./how.js'),
  changes: () => import('./changes.js'),
  code: () => import('./code.js'),
  about: () => import('./about.js'),
});
$('#mode').textContent = isStatic() ? 'static site' : 'local app';
start();
