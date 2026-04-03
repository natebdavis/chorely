import { useState } from "react";
import { StyleSheet, Text, TouchableOpacity, View } from "react-native";

import { Chore } from "./ChoreContext";

const STATUSES = ["UNASSIGNED", "IN_PROGRESS", "COMPLETE"];

const STATUS_COLORS: Record<string, string> = {
  UNASSIGNED: "#6B7280",
  IN_PROGRESS: "#F59E0B",
  COMPLETE: "#10B981",
};

type Member = {
  userid: number;
  username: string;
  fname: string;
  lname: string;
};

type ChoreItemProps = {
  chore: Chore;
  onComplete: () => void;
  onStatusChange: (choreId: string, newStatus: string, assigneeId?: number | null) => void;
  showDropdownFor: string | null;
  onToggleDropdown: (choreId: string | null) => void;
  members: Member[];
};

export function ChoreItem({ chore, onComplete, onStatusChange, showDropdownFor, onToggleDropdown, members }: ChoreItemProps) {
  const isOpen = showDropdownFor === chore.id;
  const statusColor = STATUS_COLORS[chore.status ?? "UNASSIGNED"] ?? "#6B7280";
  const isUnassigned = chore.assignedTo === "Unassigned";
  const [showAssigneePicker, setShowAssigneePicker] = useState(false);

  const handleClose = () => {
    setShowAssigneePicker(false);
    onToggleDropdown(null);
  };

  return (
    <View style={styles.card}>
      <View style={styles.content}>
        <Text style={styles.title}>{chore.name}</Text>
        <Text style={styles.assignee}>Assigned to: {chore.assignedTo}</Text>
        <Text style={styles.meta}>Request date: {chore.requestDate ?? "Unknown"}</Text>
        <Text style={styles.meta}>Due date: {chore.dueDate ?? "Unknown"}</Text>

        {/* Status badge — tap to open dropdown */}
        <TouchableOpacity
          style={[styles.statusBadge, { backgroundColor: statusColor }]}
          onPress={() => {
            setShowAssigneePicker(false);
            onToggleDropdown(isOpen ? null : chore.id);
          }}
        >
          <Text style={styles.statusText}>{chore.status ?? "Unknown"}</Text>
        </TouchableOpacity>

        {/* Status dropdown */}
        {isOpen && !showAssigneePicker && (
          <View style={styles.dropdown}>
            {STATUSES.filter((s) => !(s === "IN_PROGRESS" && isUnassigned)).map((s) => (
              <TouchableOpacity
                key={s}
                style={styles.dropdownItem}
                onPress={() => {
                  onStatusChange(chore.id, s);
                  handleClose();
                }}
              >
                <Text style={[styles.dropdownText, { color: STATUS_COLORS[s] }]}>{s}</Text>
              </TouchableOpacity>
            ))}

            {/* Assign & Start — only shown when unassigned */}
            {isUnassigned && (
              <TouchableOpacity
                style={styles.dropdownItem}
                onPress={() => setShowAssigneePicker(true)}
              >
                <Text style={[styles.dropdownText, { color: STATUS_COLORS["IN_PROGRESS"] }]}>
                  Assign & Start
                </Text>
              </TouchableOpacity>
            )}
          </View>
        )}

        {/* Assignee picker — shown after tapping "Assign & Start" */}
        {isOpen && showAssigneePicker && (
          <View style={styles.dropdown}>
            <TouchableOpacity style={styles.dropdownItem} onPress={() => setShowAssigneePicker(false)}>
              <Text style={[styles.dropdownText, { color: "#6B7280" }]}>← Back</Text>
            </TouchableOpacity>
            {members.map((member) => (
              <TouchableOpacity
                key={member.userid}
                style={styles.dropdownItem}
                onPress={() => {
                  onStatusChange(chore.id, "IN_PROGRESS", member.userid);
                  handleClose();
                }}
              >
                <Text style={styles.dropdownText}>
                  {member.fname} {member.lname} (@{member.username})
                </Text>
              </TouchableOpacity>
            ))}
          </View>
        )}

        <Text style={styles.description}>{chore.description}</Text>
      </View>
    </View>
  );
}

const styles = StyleSheet.create({
  card: {
    backgroundColor: "white",
    borderRadius: 20,
    padding: 18,
    marginBottom: 14,
    shadowColor: "#000",
    shadowOffset: { width: 0, height: 2 },
    shadowOpacity: 0.15,
    shadowRadius: 5,
    elevation: 5,
  },
  content: {
    marginBottom: 4,
  },
  title: {
    fontSize: 18,
    fontWeight: "bold",
    color: "#111827",
    marginBottom: 8,
  },
  description: {
    fontSize: 14,
    color: "#4B5563",
    lineHeight: 20,
    marginTop: 8,
  },
  assignee: {
    fontSize: 13,
    color: "#6B7280",
    fontWeight: "600",
    marginBottom: 8,
  },
  meta: {
    fontSize: 13,
    color: "#6B7280",
    marginBottom: 6,
  },
  statusBadge: {
    alignSelf: "flex-start",
    paddingHorizontal: 12,
    paddingVertical: 5,
    borderRadius: 20,
    marginTop: 6,
    marginBottom: 4,
  },
  statusText: {
    color: "white",
    fontSize: 12,
    fontWeight: "600",
  },
  dropdown: {
    backgroundColor: "white",
    borderRadius: 12,
    borderWidth: 1,
    borderColor: "#ddd",
    marginTop: 6,
    marginBottom: 4,
    overflow: "hidden",
  },
  dropdownItem: {
    padding: 12,
    borderBottomWidth: 1,
    borderBottomColor: "#eee",
  },
  dropdownText: {
    fontSize: 13,
    fontWeight: "600",
  },
});
