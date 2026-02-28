// SPDX-License-Identifier: MIT
pragma solidity ^0.8.20;

/**
 * @title ClaimRegistry
 * @notice Minimal decentralized claim registry + wallet-based voting.
 * @dev No admin roles, no tokenomics, no upgradeability.
 */
contract ClaimRegistry {
    struct Claim {
        uint256 trueVotes;
        uint256 falseVotes;
        bool exists;
        mapping(address => bool) hasVoted;
    }

    mapping(bytes32 => Claim) private claims;

    error ClaimAlreadyExists(bytes32 claimHash);
    error ClaimDoesNotExist(bytes32 claimHash);
    error AlreadyVoted(address voter, bytes32 claimHash);

    event ClaimRegistered(bytes32 indexed claimHash);
    event VoteCast(address indexed voter, bytes32 indexed claimHash, bool voteTrue);

    /**
     * @notice Register a claim hash if it does not exist yet.
     */
    function registerClaim(bytes32 _claimHash) external {
        Claim storage claim = claims[_claimHash];
        if (claim.exists) revert ClaimAlreadyExists(_claimHash);

        claim.exists = true;
        emit ClaimRegistered(_claimHash);
    }

    /**
     * @notice Vote that an existing claim is true.
     */
    function voteTrue(bytes32 _claimHash) external {
        _vote(_claimHash, true);
    }

    /**
     * @notice Vote that an existing claim is false.
     */
    function voteFalse(bytes32 _claimHash) external {
        _vote(_claimHash, false);
    }

    /**
     * @notice Return vote totals for a claim hash.
     */
    function getVotes(bytes32 _claimHash) external view returns (uint256 trueVotes, uint256 falseVotes) {
        Claim storage claim = claims[_claimHash];
        if (!claim.exists) revert ClaimDoesNotExist(_claimHash);
        return (claim.trueVotes, claim.falseVotes);
    }

    /**
     * @notice Check whether a claim hash has been registered.
     */
    function claimExists(bytes32 _claimHash) external view returns (bool) {
        return claims[_claimHash].exists;
    }

    /**
     * @notice Check whether a wallet has voted on a claim hash.
     */
    function hasAddressVoted(bytes32 _claimHash, address _voter) external view returns (bool) {
        Claim storage claim = claims[_claimHash];
        if (!claim.exists) revert ClaimDoesNotExist(_claimHash);
        return claim.hasVoted[_voter];
    }

    function _vote(bytes32 _claimHash, bool voteAsTrue) internal {
        Claim storage claim = claims[_claimHash];
        if (!claim.exists) revert ClaimDoesNotExist(_claimHash);
        if (claim.hasVoted[msg.sender]) revert AlreadyVoted(msg.sender, _claimHash);

        claim.hasVoted[msg.sender] = true;
        if (voteAsTrue) {
            claim.trueVotes += 1;
        } else {
            claim.falseVotes += 1;
        }

        emit VoteCast(msg.sender, _claimHash, voteAsTrue);
    }
}
