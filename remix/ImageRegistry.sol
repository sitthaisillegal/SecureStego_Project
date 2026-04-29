// SPDX-License-Identifier: MIT
pragma solidity ^0.8.0;

contract ImageRegistry {
    
    // We create a structure to hold the details of our stego image
    struct StegoRecord {
        string fileHash;      // The SHA-256 fingerprint
        address owner;        // The wallet address of the person who uploaded it
        uint256 timestamp;    // The exact time it was registered
        bool isRegistered;    // A simple true/false check
    }

    // This creates a searchable database linking the hash to its record
    mapping(string => StegoRecord) public records;

    // This creates a log that the blockchain broadcasts when a file is stored
    event HashRegistered(string fileHash, address owner, uint256 timestamp);

    // --- FUNCTION 1: STORE THE HASH ---
    function registerHash(string memory _fileHash) public {
        // Make sure this hash hasn't already been saved
        require(!records[_fileHash].isRegistered, "This file hash is already registered on the blockchain!");

        // Save the details to our blockchain database
        records[_fileHash] = StegoRecord({
            fileHash: _fileHash,
            owner: msg.sender,
            timestamp: block.timestamp,
            isRegistered: true
        });

        // Broadcast the success event
        emit HashRegistered(_fileHash, msg.sender, block.timestamp);
    }

    // --- FUNCTION 2: VERIFY THE HASH ---
    function verifyHash(string memory _fileHash) public view returns (bool, address, uint256) {
        // If the hash exists, return true, the owner, and the time it was saved
        if (records[_fileHash].isRegistered) {
            return (true, records[_fileHash].owner, records[_fileHash].timestamp);
        } else {
            // If it doesn't exist (file was tampered with!), return false
            return (false, address(0), 0);
        }
    }
}