# ADR 0003: Use ChromaDB for Phase 1 (with Qdrant for Phase 2)

- **Date**: 2026-04-16
- **Status**: Accepted
- **Deciders**: Project Lead

## Context

We need a vector database to store document embeddings for retrieval. Requirements:
- Zero-configuration setup for rapid prototyping
- Local/offline operation (no cloud dependency)
- Persistent storage (survive restarts)
- Python-native (fits our stack)
- Scalable enough for Phase 1 (20-30 documents, ~5K chunks)
- Upgrade path to production scale (100K+ chunks)

## Decision

We will use **ChromaDB** for Phase 1, with a migration path to **Qdrant** for Phase 2/3 when scaling requirements increase.

## Consequences

### Positive
- **Zero setup**: Runs in-process, no server required
- **Pure Python**: No additional dependencies, easy installation
- **Persistent**: Stores data on disk automatically
- **LlamaIndex integration**: First-class support via `ChromaVectorStore`
- **Fast for small datasets**: Optimal for Phase 1 scale
- **Free**: No cost for local development

### Negative
- **Not for large scale**: Performance degrades with millions of documents
- **Single-node only**: No clustering support
- **Memory usage**: Loads data into RAM (manageable for Phase 1)
- **Limited features**: Basic compared to enterprise vector DBs

### Neutral
- Apache 2.0 license
- In-memory with persistence option

## Phase-Based Strategy

| Phase | Documents | Chunks | Database | Why |
|-------|-----------|--------|----------|-----|
| Phase 1 | 30 | ~5,000 | ChromaDB | Zero setup, fast iteration |
| Phase 2 | 200 | ~50,000 | ChromaDB → Qdrant | Qdrant for production features |
| Phase 3 | 1000+ | ~250,000 | Qdrant Cloud | Scale, clustering, managed |

## Migration Path

ChromaDB and Qdrant are conceptually similar (both use HNSW for similarity search). Migration involves:

1. Export from ChromaDB: `collection.get()` to retrieve all embeddings
2. Transform to Qdrant format: `PointStruct` objects
3. Import to Qdrant: `client.upsert()`
4. Update LlamaIndex: Swap `ChromaVectorStore` for `QdrantVectorStore`

**Estimated migration effort**: 1-2 days

## Alternatives Considered

### Alternative 1: Qdrant (for all phases)
- **Pros**: Production-ready, fast, supports filtering, hybrid search, clustering
- **Cons**: Requires Docker or cloud service, more setup complexity
- **Why rejected**: Overkill for Phase 1. ChromaDB is sufficient and faster to set up.
- **Resolution**: Will use Qdrant for Phase 2/3

### Alternative 2: Weaviate
- **Pros**: GraphQL interface, hybrid search, multimodal
- **Cons**: Heavier resource usage, more complex setup
- **Why rejected**: More suited for enterprise with dedicated infrastructure team

### Alternative 3: Pinecone
- **Pros**: Fully managed, auto-scaling, serverless
- **Cons**: Cloud-only (no local), costs money, data leaves premises
- **Why rejected**: Core requirement is offline/local operation

### Alternative 4: FAISS
- **Pros**: Facebook's library, extremely fast
- **Cons**: Low-level API, more code to write, no persistence by default
- **Why rejected**: LlamaIndex integration not as mature, more development work

## Implementation Notes

```python
from llama_index.vector_stores.chroma import ChromaVectorStore
import chromadb

# Setup
chroma_client = chromadb.PersistentClient(path="./data/chroma_db")
collection = chroma_client.get_or_create_collection("iks_corpus")
vector_store = ChromaVectorStore(chroma_collection=collection)

# Migration to Qdrant (Phase 2)
# from llama_index.vector_stores.qdrant import QdrantVectorStore
# vector_store = QdrantVectorStore(client=qdrant_client, collection_name="iks_corpus")
```

**Storage Location**: `data/chroma_db/` (gitignored, created on first run)

**Backup Strategy**: 
- ChromaDB: Copy `data/chroma_db/` directory
- Qdrant: Built-in snapshots

## References

- [ChromaDB Documentation](https://docs.trychroma.com/)
- [Qdrant Documentation](https://qdrant.tech/documentation/)
- [LlamaIndex Vector Stores](https://docs.llamaindex.ai/en/stable/module_guides/storing/vector_stores.html)
- [HNSW Algorithm](https://arxiv.org/abs/1603.09320) (used by both ChromaDB and Qdrant)

## Related Decisions

- ADR-0001: LlamaIndex (supports both ChromaDB and Qdrant)
- Phase 2 will evaluate Qdrant based on Phase 1 learnings
