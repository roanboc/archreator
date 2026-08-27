-- The neighbourhood of one element: everything within :depth hops, and the
-- relationships among it.
--
-- **This file is the traversal, and it has exactly one copy.** `query_model.py`
-- executes it through `sqlite3`; the navigator executes the same text through
-- sql.js against the same database. A walk written twice — once in Python for
-- the terminal and once in JavaScript for the page — is the drift
-- `model_graph.py` exists to prevent, one level up, and the browser copy is the
-- one nobody would have tested. See scope document 7, GAP6.
--
-- Parameters: :root, :depth. `:root` is a **qualified** identifier —
-- `product-archreator::ACMP1` — because a walk crosses models now and an
-- unqualified one would be ambiguous the moment two models shared a `G1`.
--
-- The walk is **undirected**. Direction in this model is a property of the
-- sentence rather than of the relationship: a catalogue states a connection
-- from whichever end owns the row, so `Provided by` and `Provides` are one
-- relationship written from two sides. "What would this change touch" does not
-- care which way somebody phrased it.
--
-- It is also **model-blind**. An edge whose far end names another model is
-- followed like any other, which is the whole of what scope document 9
-- delivered: a blast radius that stops at a repository boundary is a wrong
-- answer, not a smaller one.
WITH RECURSIVE
link(a, b, rel, origin, pending, doc) AS (
    SELECT
        e.project || '::' || e.src,
        CASE WHEN e.dst_project = '' THEN e.project ELSE e.dst_project END
            || '::' || e.dst,
        e.rel, e.origin, e.pending, e.doc
    FROM edges e
),
walk(id, hop) AS (
    SELECT :root, 0
    UNION
    SELECT CASE WHEN l.a = w.id THEN l.b ELSE l.a END, w.hop + 1
    FROM walk w
    JOIN link l ON l.a = w.id OR l.b = w.id
    WHERE w.hop < :depth
),
-- UNION above dedupes (id, hop) pairs, not ids: one element reached at two
-- depths appears twice. The nearest arrival is the one that describes it.
reach(id, hop) AS (SELECT id, MIN(hop) FROM walk GROUP BY id),
node(gid, project, id, name, type, layer_group, doc) AS (
    SELECT project || '::' || id, project, id, name, type, layer_group, doc
    FROM nodes
)
SELECT
    l.a      AS src,
    ns.project AS src_model,
    ns.id    AS src_local,
    ns.name  AS src_name,
    ns.type  AS src_type,
    ns.layer_group AS src_group,
    ns.doc   AS src_doc,
    rs.hop   AS src_hop,
    l.b      AS dst,
    nd.project AS dst_model,
    nd.id    AS dst_local,
    nd.name  AS dst_name,
    nd.type  AS dst_type,
    nd.layer_group AS dst_group,
    nd.doc   AS dst_doc,
    rd.hop   AS dst_hop,
    l.rel,
    l.origin,
    l.pending,
    l.doc    AS edge_doc
FROM link l
JOIN reach rs ON rs.id = l.a
JOIN reach rd ON rd.id = l.b
LEFT JOIN node ns ON ns.gid = l.a
LEFT JOIN node nd ON nd.gid = l.b
ORDER BY MIN(rs.hop, rd.hop), l.a, l.b;
