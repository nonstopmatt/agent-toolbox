# Container and self-hosted service branch [#37]

A pinned image tag pins the image, not what the image downloads when it starts.

1. **Find the unpinned edges.** Grep the start path (entrypoint, CMD, and every script they
   call) for run-time dependency resolution: `npx`, `pnpx` / `pnpm dlx`, `pip install`,
   `go run`, `curl | sh`, an unpinned `apt-get install`. Name each one in the install report.
   Where the dependency is already vendored inside the image, redirect that one call to the
   vendored copy with a `command:` override in the compose file, commented with the upstream
   condition that lets it be removed. That keeps the fix visible, survives recreation, and
   does not fork the image.
2. **Prove the whole path with one real request.** Pick a request whose correct answer needs
   proxy, app and database together; a login POST with deliberately wrong credentials that
   returns the app's own "invalid user name or password" is the model. `running`, `healthy`,
   restart counts and health checks are claims about processes, not about the service.
3. **Keep the kit's boundary.** A service meant to bind localhost stays on 127.0.0.1; a port
   answering 200 is evidence about the port, not about which service is on it.
