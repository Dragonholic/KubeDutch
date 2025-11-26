// SPDX-License-Identifier: MIT
pragma solidity ^0.8.19;

contract UsageLedger {
    address public owner;

    event UsageLogged(
        string indexed username,
        uint256 duration,
        uint256 cost,
        uint256 timestamp
    );

    modifier onlyOwner() {
        require(msg.sender == owner, "Caller is not the owner");
        _;
    }

    constructor() {
        owner = msg.sender;
    }

    function logUsage(
        string memory _username, 
        uint256 _duration, 
        uint256 _cost
    ) public onlyOwner {
        emit UsageLogged(_username, _duration, _cost, block.timestamp);
    }

    function transferOwnership(address newOwner) public onlyOwner {
        require(newOwner != address(0), "New owner is the zero address");
        owner = newOwner;
    }
}

