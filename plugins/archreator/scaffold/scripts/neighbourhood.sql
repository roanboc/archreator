-- The neighbourhood of one element: everything within :depth hops, and the
-- relationships among it.
--
-- **This file is the traversal, and it has exactly one copy.** `query_model.py`
-- executes it through `sqlite3`; the navigator executes the same text through
-- sql.js against the same database. A walk written twice — once in Python for
-- the terminal and once in JavaScript for the page — is the drift `model_graph.py`
-- exists to prevent, one level up, and the browser copy is the one nobody would
-- have tested. See scope document 7, GAP6.
--
-- Parameters: :project, :root, :depth.
--
-- The walk is **undirected**. Direction in this model is a property of the
-- sentence rather than of the relationship: a catalogue states a connection
-- from whichever end owns the row, so `Provided by` and `Provides` are one
-- relationship written from two sides. "What would this change touch" does not
-- care which way somebody phrased it.
WITH RECURSIVE
walk(id, hop) AS (
    SELECT :root, 0
    UNION
    SELECT CASE WHEN e.src = w.id THEN e.dst ELSE e.src END, w.hop + 1
    FROM walk w
    JOIN edges e
      ON e.project = :project AND (e.src = w.id OR e.dst = w.id)
    WHERE w.hop < :depth
),
-- UNION above dedupes (id, hop) pairs, not ids: one element reached at two
-- depths appears twice. The nearest arrival is the one that describes it.
reach(id, hop) AS (SELECT id, MIN(hop) FROM walk GROUP BY id)
SELECT
    e.src,
    ns.name  AS src_name,
    ns.type  AS src_type,
    ns.layer_group AS src_group,
    ns.doc   AS src_doc,
    rs.hop   AS src_hop,
    e.dst,
    nd.name  AS dst_name,
    nd.type  AS dst_type,
    nd.layer_group AS dst_group,
    nd.doc   AS dst_doc,
    rd.hop   AS dst_hop,
    e.rel,
    e.origin,
    e.pending,
    e.doc    AS edge_doc
FROM edges e
JOIN reach rs ON rs.id = e.src
JOIN reach rd ON rd.id = e.dst
LEFT JOIN nodes ns ON ns.project = e.project AND ns.id = e.src
LEFT JOIN nodes nd ON nd.project = e.project AND nd.id = e.dst
WHERE e.project = :project
ORDER BY MIN(rs.hop, rd.hop), e.src, e.dst;
