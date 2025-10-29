function syncRepoRoot(bytes32 repoDigest, string memory proofFile) external onlyFlameholder {
    emit RepoRootSynced(repoDigest, proofFile);
}