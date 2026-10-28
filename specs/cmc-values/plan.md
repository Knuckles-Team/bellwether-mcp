# CONN-BELLWETHER-MCP-CMC-VALUES — Design and implementation plan

Governing spec: [spec.md](spec.md).

Validate numeric fields as they are normalized for listings, quotes and global metrics. Preserve a null when the provider does not supply a value. Refuse malformed numeric values before the served tool returns a page.

Each endpoint requires its expected data container. Global metrics also require a nonempty USD quote, so a missing payload cannot become a fabricated snapshot. Empty listing and quote collections remain valid.

Listing and quote records require a positive integer provider ID before it is rendered as the stable record identity.

Listings and quote pages refuse duplicate asset identities, including duplicates with different values. Cross-page uniqueness is a separate concern.
