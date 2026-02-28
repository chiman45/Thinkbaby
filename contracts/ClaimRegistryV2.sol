// SPDX-License-Identifier: MIT
pragma solidity ^0.8.20;

/**
 * @title ClaimRegistryV2
 * @notice Role-enforced decentralized claim registry:
 * - Users register claims
 * - Validators vote true/false
 * @dev No admin role. Roles are self-selected once per wallet.
 */
contract ClaimRegistryV2 {
    enum Role {
        None,
        User,
        Validator
    }

    struct Claim {
        uint256 trueVotes;
        uint256 falseVotes;
        uint256 validatorTrueVotes;
        uint256 validatorFalseVotes;
        bool exists;
        address submitter;
        mapping(address => bool) hasVoted;
    }

    mapping(address => Role) private roles;
    mapping(bytes32 => Claim) private claims;

    error AlreadyRegistered(address account);
    error NotUser(address account);
    error NotValidator(address account);
    error ClaimAlreadyExists(bytes32 claimHash);
    error ClaimDoesNotExist(bytes32 claimHash);
    error AlreadyVoted(address voter, bytes32 claimHash);
    error SubmitterCannotVote(address submitter, bytes32 claimHash);

    event RoleRegistered(address indexed account, Role role);
    event ClaimRegistered(bytes32 indexed claimHash, address indexed submitter);
    event VoteCast(address indexed voter, bytes32 indexed claimHash, bool voteTrue);

    /**
     * @notice Self-register as a User. One role per wallet.
     */
    function registerAsUser() external {
        if (roles[msg.sender] != Role.None) revert AlreadyRegistered(msg.sender);
        roles[msg.sender] = Role.User;
        emit RoleRegistered(msg.sender, Role.User);
    }

    /**
     * @notice Self-register as a Validator. One role per wallet.
     */
    function registerAsValidator() external {
        if (roles[msg.sender] != Role.None) revert AlreadyRegistered(msg.sender);
        roles[msg.sender] = Role.Validator;
        emit RoleRegistered(msg.sender, Role.Validator);
    }

    /**
     * @notice Register claim hash. Only User role can submit.
     */
    function registerClaim(bytes32 _claimHash) external {
        if (roles[msg.sender] != Role.User) revert NotUser(msg.sender);

        Claim storage claim = claims[_claimHash];
        if (claim.exists) revert ClaimAlreadyExists(_claimHash);

        claim.exists = true;
        claim.submitter = msg.sender;
        emit ClaimRegistered(_claimHash, msg.sender);
    }

    /**
     * @notice Validator vote for true.
     */
    function voteTrue(bytes32 _claimHash) external {
        _vote(_claimHash, true);
    }

    /**
     * @notice Validator vote for false.
     */
    function voteFalse(bytes32 _claimHash) external {
        _vote(_claimHash, false);
    }

    /**
     * @notice Alias requested by product team.
     */
    function voteTrueValid(bytes32 _claimHash) external {
        _vote(_claimHash, true);
    }

    /**
     * @notice Alias requested by product team.
     */
    function voteFalseFake(bytes32 _claimHash) external {
        _vote(_claimHash, false);
    }

    /**
     * @notice Total vote counts (same as V1 shape).
     */
    function getVotes(bytes32 _claimHash) external view returns (uint256 trueVotes, uint256 falseVotes) {
        Claim storage claim = claims[_claimHash];
        if (!claim.exists) revert ClaimDoesNotExist(_claimHash);
        return (claim.trueVotes, claim.falseVotes);
    }

    /**
     * @notice Validator-only counters for direct UI/bot consumption.
     */
    function getValidatorVotes(bytes32 _claimHash)
        external
        view
        returns (uint256 validatorTrueVotes, uint256 validatorFalseVotes)
    {
        Claim storage claim = claims[_claimHash];
        if (!claim.exists) revert ClaimDoesNotExist(_claimHash);
        return (claim.validatorTrueVotes, claim.validatorFalseVotes);
    }

    function claimExists(bytes32 _claimHash) external view returns (bool) {
        return claims[_claimHash].exists;
    }

    function hasAddressVoted(bytes32 _claimHash, address _voter) external view returns (bool) {
        Claim storage claim = claims[_claimHash];
        if (!claim.exists) revert ClaimDoesNotExist(_claimHash);
        return claim.hasVoted[_voter];
    }

    function getRole(address _account) external view returns (Role) {
        return roles[_account];
    }

    function getClaimSubmitter(bytes32 _claimHash) external view returns (address) {
        Claim storage claim = claims[_claimHash];
        if (!claim.exists) revert ClaimDoesNotExist(_claimHash);
        return claim.submitter;
    }

    function _vote(bytes32 _claimHash, bool voteAsTrue) internal {
        if (roles[msg.sender] != Role.Validator) revert NotValidator(msg.sender);

        Claim storage claim = claims[_claimHash];
        if (!claim.exists) revert ClaimDoesNotExist(_claimHash);
        if (claim.submitter == msg.sender) revert SubmitterCannotVote(msg.sender, _claimHash);
        if (claim.hasVoted[msg.sender]) revert AlreadyVoted(msg.sender, _claimHash);

        claim.hasVoted[msg.sender] = true;

        if (voteAsTrue) {
            claim.trueVotes += 1;
            claim.validatorTrueVotes += 1;
        } else {
            claim.falseVotes += 1;
            claim.validatorFalseVotes += 1;
        }

        emit VoteCast(msg.sender, _claimHash, voteAsTrue);
    }
}
